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
#Register
@app.route('/register_airline_staff')
def register_airline_staff():
	return render_template('register_airline_staff.html')


#Authenticates the register
@app.route('/registerStaff', methods=['GET', 'POST'])
def registerStaff():
	#grabs information from the forms
	username = request.form['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	

	airline_name = request.form['airline_name']
	airline_query = 'SELECT * FROM airline where airline_name = %s'
	cursor.execute(airline_query, (airline_name))
	airlineExists = cursor.fetchone()

	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register_airline_staff.html', error = error)
	elif(airlineExists is None):
		error = "This airline does not exist"
		return render_template('register_airline_staff.html', error = error)
	else:
		password = hashlib.md5(request.form['password'].encode()).hexdigest()
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		date_of_birth = request.form['date_of_birth']
		insert_staff_query = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(insert_staff_query, (airline_name, username, password, first_name, last_name, date_of_birth))

		#put phone numbers in staff_phone set
		phone_numbers = request.form.getlist('staff_phone[]')
		insert_phone_query = 'INSERT INTO staff_phone VALUES(%s, %s)'
		phone_already_query = 'SELECT * from staff_phone where username = %s and phone_num = %s'
		for phone in phone_numbers:
			cursor.execute(phone_already_query, (username, phone))
			phoneExists = cursor.fetchone();
			if(phoneExists is None):
				cursor.execute(insert_phone_query, (username, phone))


		#put emails in staff_email
		emails = request.form.getlist('staff_email[]')
		insert_email_query = 'INSERT INTO staff_email VALUES(%s, %s)'
		email_already_query = 'SELECT * from staff_email where username = %s and email_id = %s'
		for email in emails:
			cursor.execute(email_already_query, (username, email))
			emailExists = cursor.fetchone();
			if(emailExists is None):
				cursor.execute(insert_email_query, (username, email))

		session['username'] = username
		session['password'] = password
		
		conn.commit()
		cursor.close()
		return redirect(url_for('customer_home'))
	

@app.route('/login_airline_staff')
def login_airline_staff():
	return render_template('login_airline_staff.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginStaff():
	#grabs information from the forms
	username = request.form['username']
	password = hashlib.md5(request.form['password'].encode()).hexdigest()


	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airline_staff WHERE username = %s and pwd = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['password'] = password
		return redirect(url_for('customer_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login_airline_staff.html', error=error)


@app.route('/customer_home')
def customer_home():
	return render_template('customer_home.html', username = session['username'])

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









#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')



#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
