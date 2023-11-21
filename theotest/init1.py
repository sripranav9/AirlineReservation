#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_DDB2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')


################################################################################################################################
#Airline Staff

##################################################
#REGISTER
@app.route('/register_airline_staff')
def register_airline_staff():
	return render_template('register_airline_staff.html')


#Registers Staff -> puts data into database only if allowed
@app.route('/registerStaff', methods=['GET', 'POST'])
def registerStaff():

	#get query to see whether username already exists
	username = request.form['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	usernameExists = cursor.fetchone()
	
	#get query to see whether airline exists
	airline_name = request.form['airline_name']
	airline_query = 'SELECT * FROM airline where airline_name = %s'
	cursor.execute(airline_query, (airline_name))
	airlineExists = cursor.fetchone()

	error = None
	if(usernameExists):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register_airline_staff.html', error = error)
	elif(airlineExists is None):
		error = "This airline does not exist"
		return render_template('register_airline_staff.html', error = error)

	#if neither of the errors above occur add data to database
	else:

		#insert given user data into airline_staff 
		password = hashlib.md5(request.form['password'].encode()).hexdigest()
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		date_of_birth = request.form['date_of_birth']
		insert_staff_query = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(insert_staff_query, (airline_name, username, password, first_name, last_name, date_of_birth))

		#insert unique phone numbers into staff_phone set
		phone_numbers = request.form.getlist('staff_phone[]')
		insert_phone_query = 'INSERT INTO staff_phone VALUES(%s, %s)'
		phone_already_query = 'SELECT * from staff_phone where username = %s and phone_num = %s'
		for phone in phone_numbers:
			cursor.execute(phone_already_query, (username, phone))
			phoneExists = cursor.fetchone();
			if(phoneExists is None):
				cursor.execute(insert_phone_query, (username, phone))


		#insert unique emails in staff_email
		emails = request.form.getlist('staff_email[]')
		insert_email_query = 'INSERT INTO staff_email VALUES(%s, %s)'
		email_already_query = 'SELECT * from staff_email where username = %s and email_id = %s'
		for email in emails:
			cursor.execute(email_already_query, (username, email))
			emailExists = cursor.fetchone();
			if(emailExists is None):
				cursor.execute(insert_email_query, (username, email))

		#if they register they automatically are logged in
		session['username'] = username
		session['password'] = password
		
		conn.commit()
		cursor.close()
		return redirect(url_for('staff_home'))

##################################################


##################################################
#LOGIN

@app.route('/login_airline_staff')
def login_airline_staff():
	return render_template('login_airline_staff.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginStaff():

	#grabs information from the forms
	username = request.form['username']
	password = hashlib.md5(request.form['password'].encode()).hexdigest()

	#queries database to see if such tuple exists
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and pwd = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()


	error = None

	if(data):
		#if tuple exists create a session for the the user and login
		session['username'] = username
		session['password'] = password
		return redirect(url_for('staff_home'))
	else:
		#if tuple doesn't exist then throw error message
		error = 'Invalid login or username'
		return render_template('login_airline_staff.html', error=error)

##################################################

#If the staff exists then returns false if Staff does not exist return True or if Session is not open return True
def isNotValidStaff():
	if(len(session) == 0): return True
	if(session['username'] is None): return True
	if(session['password'] is None): return True
	username = session['username']
	password = session['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and pwd = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()
	if(data is None): return True
	return False


@app.route('/staff_home')
def staff_home():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('staff_home.html', username = session['username'])

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('hello'))
##################################################




























################################################################################################################################




@app.route('/search_for_flights')
def search_for_flights():
	return render_template('search_for_flights.html')

@app.route('/searchForFlights', methods=['GET', 'POST'])
def searchForFlights():
	src_airport1 = request.form['src_airport']
	dst_airport1 = request.form['dst_airport']
	dep_date = request.form['departure_date']
	ret_date = request.form['return_date']
	trip_type = request.form['trip_type']
	cursor = conn.cursor()

	outgoing_query = 'SELECT * From flight Where departure_airport = %s and arrival_airport = %s and departure_date = %s'
	cursor.execute(outgoing_query, (src_airport1, dst_airport1, dep_date))
	outgoing_flights = cursor.fetchall()
	final_outgoing_flights = []

	#To check to see if no tickets are available and then to check to see 
	for flight in outgoing_flights:
		
		#All of the tickets
		num_tickets_query = 'SELECT count(*) as "all" from ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
		cursor.execute(num_tickets_query, (flight['airline_name'], flight['flight_num'], flight['departure_date'], flight['departure_time']))
		num_tickets = cursor.fetchone()

		#
		tickets_purchased_query = 'SELECT count(*) as "bought" from purchase WHERE ticketID in (SELECT ticketID from ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
		cursor.execute(tickets_purchased_query, (flight['airline_name'], flight['flight_num'], flight['departure_date'], flight['departure_time']))
		purchased_tickets = cursor.fetchone()


		remaining_tickets = num_tickets['all'];

		if(purchased_tickets):
			remaining_tickets -= purchased_tickets['bought']

		if(remaining_tickets/num_tickets['all'] <= 0.2):
			flight['base_price_ticket'] = round(float(flight['base_price_ticket']) * 1.25,2)

		#status != canceled 
		if(remaining_tickets != 0):
			final_outgoing_flights.append(flight)
		

	return_query = 'SELECT * From flight Where departure_airport = %s and arrival_airport = %s and departure_date = %s'
	cursor.execute(return_query, (dst_airport1, src_airport1, ret_date))
	return_flights = cursor.fetchall()

	cursor.close()
	if(trip_type == 'one_way'):
		return render_template('search_for_flights.html', outBoundFlights=final_outgoing_flights, trip_type = 'one_way')
	
	return render_template('search_for_flights.html', outBoundFlights=final_outgoing_flights, returnBoundFlights=return_flights, trip_type = 'round_trip')






		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
