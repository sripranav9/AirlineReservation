#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
from datetime import datetime

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_DDB3',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def home():
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
			if(phone == ''): continue
			cursor.execute(phone_already_query, (username, phone))
			phoneExists = cursor.fetchone();
			if(phoneExists is None):
				cursor.execute(insert_phone_query, (username, phone))


		#insert unique emails in staff_email
		emails = request.form.getlist('staff_email[]')
		insert_email_query = 'INSERT INTO staff_email VALUES(%s, %s)'
		email_already_query = 'SELECT * from staff_email where username = %s and email_id = %s'
		for email in emails:
			if(email == ''): continue
			cursor.execute(email_already_query, (username, email))
			emailExists = cursor.fetchone();
			if(emailExists is None):
				cursor.execute(insert_email_query, (username, email))

		#if they register they automatically are logged in
		session['username'] = username
		session['password'] = password
		session['first_name'] = first_name
		session['airline'] = airline_name
		
		conn.commit()
		cursor.close()
		return redirect(url_for('staff_home'))

##################################################


##################################################
#LOGIN

@app.route('/login_airline_staff')
def login_airline_staff():
	return render_template('login_airline_staff.html')

@app.route('/loginStaff', methods=['GET', 'POST'])
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
		session['airline'] = data['airline_name']
		session['first_name'] = data['first_name']
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
	return render_template('staff_home.html', username = session['first_name'])

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))

@app.route('/view_flights')
def view_flights():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	thirty_day_query = 'SELECT * FROM flight WHERE airline_name = %s and CURRENT_DATE <= departure_date and departure_date <= DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY) ORDER BY departure_date DESC'
	cursor.execute(thirty_day_query, (session['airline']))
	thirty_day_flights = cursor.fetchall()
	cursor.close()
	message = "Flights in next 30 days"
	return render_template('view_flights.html', outBoundFlights = thirty_day_flights, message = message)

@app.route('/viewFlights', methods=['GET', 'POST'])
def viewFlights():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	flight_num = request.form.get('flight_num')
	start_date = request.form.get('start_date')
	end_date = request.form.get('end_date')
	departure_airport = request.form.get('departure_airport')
	arrival_airport = request.form.get('arrival_airport')

	search_flight_query = "SELECT * FROM flight WHERE "
	conditions = []
	query_conditions = []

	if flight_num:
		conditions.append("flight_num = %s")
		query_conditions.append(flight_num)
	if start_date and end_date:
		conditions.append("departure_date BETWEEN %s AND %s")
		query_conditions.append(start_date)
		query_conditions.append(end_date)
	elif start_date:
		conditions.append("departure_date >= %s")
		query_conditions.append(start_date)
	elif end_date:
		conditions.append("departure_date <= %s")
		query_conditions.append(end_date)
	if(departure_airport):
		conditions.append("departure_airport = %s")
		query_conditions.append(departure_airport)
	if(arrival_airport):
		conditions.append("arrival_airport = %s")
		query_conditions.append(arrival_airport)

	conditions.append("airline_name = %s")
	query_conditions.append(session['airline'])

	if conditions:
		search_flight_query += " AND ".join(conditions)

	cursor.execute(search_flight_query, tuple(query_conditions))
	searchResults = cursor.fetchall()
	message = "Here are the results for your query"

	for flight in searchResults:
		current_date = datetime.now().date()
		current_time = datetime.now().time()
		dep_time_string = str(flight['departure_time'])


		departure_time_nonString = datetime.strptime(dep_time_string, '%H:%M:%S').time()
		if(current_date > flight['departure_date']):
			flight['review'] = 'Reviews'
		elif(current_date == flight['departure_date'] and current_time >= departure_time_nonString):
			flight['review'] = 'Reviews'
		


	return render_template('view_flights.html', outBoundFlights = searchResults, message = message)

@app.route('/change_status', methods=['GET'])
def change_status():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
	cursor.execute(flight_query, (request.args.get('param2'), request.args.get('param1'), request.args.get('param3'), request.args.get('param4')))
	flight = cursor.fetchone()
	cursor.close()


	return render_template('change_status.html', flight = flight)


@app.route('/changeStatus', methods=['GET','POST'])
def changeStatus():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	selected_status = request.form['status']
	cursor = conn.cursor()

	flight_change_query = 'UPDATE flight set flight_status = %s where airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
	flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'

	airline_name = request.form.get('airline_name')
	flight_num = request.form.get('flight_num')
	departure_date = request.form.get('departure_date')
	departure_time = request.form.get('departure_time')

	cursor.execute(flight_change_query, (selected_status, airline_name, flight_num, departure_date, departure_time))
	cursor.execute(flight_query, (airline_name, flight_num, departure_date, departure_time))
	flight = cursor.fetchone()
	conn.commit()
	cursor.close()

	return render_template('change_status.html', flight = flight)

@app.route('/see_customers', methods=['GET'])
def see_customers():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	
	airline_name = request.args.get('param2')
	flight_num = request.args.get('param1')
	departure_date = request.args.get('param3')
	departure_time = request.args.get('param4')

	cursor = conn.cursor()
	flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
	cursor.execute(flight_query, (airline_name, flight_num, departure_date, departure_time))
	flight = cursor.fetchone()

	customer_query = 'SELECT * FROM purchase where ticketID in (SELECT ticketID from ticket where airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
	cursor.execute(customer_query, (airline_name, flight_num, departure_date, departure_time))
	customers = cursor.fetchall()

	cursor.close()
	return render_template('see_customers.html', flight = flight, customers = customers)


@app.route('/create_new_flight', methods=['GET', 'POST'])
def create_new_flight():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('create_new_flight.html')

@app.route('/createNewFlight', methods=['GET','POST'])
def createNewFlight():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor();
	flight_num = request.form['flight_num']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	flight_exists_query = 'SELECT * FROM flight where airline_name = %s and flight_num = %s and departure_time = %s and departure_date = %s'
	cursor.execute(flight_exists_query, (session['airline'], flight_num, departure_time, departure_date))
	flightExists = cursor.fetchone()

	#get query to see whether arrival airport exists
	arrival_airport = request.form['arrival_airport']
	arrival_aiport_query = 'SELECT * FROM airport where code = %s'
	cursor.execute(arrival_aiport_query, (arrival_airport))
	arrivalAirportExists = cursor.fetchone()

	#get query to see whether departure airport exists
	departure_airport = request.form['departure_airport']
	departure_aiport_query = 'SELECT * FROM airport where code = %s'
	cursor.execute(departure_aiport_query, (departure_airport))
	departureAirportExists = cursor.fetchone()

	#get query to see whether Airplane exists
	assigned_airplane_airline = request.form['assigned_airplane_airline']
	airplane_ID = request.form['assigned_airplaneID']
	assigned_airplane_airline_query = 'SELECT * FROM airplane where airline_name = %s and airplaneID = %s'
	cursor.execute(assigned_airplane_airline_query, (assigned_airplane_airline, airplane_ID))
	assignedAirplane = cursor.fetchone()

	#see if flight is scheudled for maintenance
	arrival_date = request.form['arrival_date']
	arrival_time = request.form['arrival_time']
	maintenance_check_query = 'SELECT * FROM maintenance where airline_name = %s and airplaneID = %s'
	cursor.execute(maintenance_check_query, (session['airline'], airplane_ID))
	flight_maintenances = cursor.fetchall()

	arrival_date_NonStr = datetime.strptime(arrival_date, "%Y-%m-%d").date()
	departure_date_NonStr = datetime.strptime(departure_date, "%Y-%m-%d").date()
	arrival_time_NonStr = datetime.strptime(str(arrival_time), '%H:%M').time()
	departure_time_nonStr = datetime.strptime(str(departure_time), '%H:%M').time()

	if((arrival_date_NonStr, arrival_time_NonStr) <= (departure_date_NonStr, departure_time_nonStr)):
		error = "Can't have a flight land before it takes off"
		cursor.close()
		return render_template('create_new_flight.html', error = error)

	for maintenance in flight_maintenances:
		#returns true if the maintancence and flight overlap
		st_time = str(maintenance['st_time'])
		end_time = str(maintenance['end_time'])
		maintenance_start_time = datetime.strptime(st_time, '%H:%M:%S').time()
		maintenance_end_time = datetime.strptime(end_time, '%H:%M:%S').time()

		if  (arrival_date_NonStr, arrival_time_NonStr) >= (maintenance['st_date'], maintenance_start_time) and (departure_date_NonStr, departure_time_nonStr) <= (maintenance['end_date'], maintenance_end_time):
			error = "Flight Interferes with scheduled maintenance and therefore can not be created"
			cursor.close()
			return render_template('create_new_flight.html', error = error)

	
	if(flightExists is not None):
		error = "This Flight Already Exists"
		cursor.close()
		return render_template('create_new_flight.html', error = error)
	
	elif(arrivalAirportExists is None):
		error = "This Arrival Airport Does Not Exist"
		cursor.close()
		return render_template('create_new_flight.html', error = error)

	elif(departureAirportExists is None):
		error = "This Departure Aiport Does Not Exist"
		cursor.close()
		return render_template('create_new_flight.html', error = error)

	elif(assignedAirplane is None):
		error = "This Airplane Does Not Exist"
		cursor.close()
		return render_template('create_new_flight.html', error = error)

	else:
		base_price = request.form['base_price_ticket']
		selected_status = request.form['status'];
		total_seats_query = 'SELECT num_of_seats from airplane where airline_name = %s and airplaneID = %s'
		cursor.execute(total_seats_query, (assigned_airplane_airline, airplane_ID))
		total_seats = cursor.fetchone();
		insert_flight_query = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(insert_flight_query, (session['airline'], departure_airport, arrival_airport, assigned_airplane_airline, airplane_ID, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price, selected_status, total_seats['num_of_seats'], total_seats['num_of_seats']))




		conn.commit()
		
		thirty_day_query = 'SELECT * FROM flight WHERE airline_name = %s and CURRENT_DATE <= departure_date and departure_date <= DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY) ORDER BY departure_date DESC'
		cursor.execute(thirty_day_query, (session['airline']))
		thirty_day_flights = cursor.fetchall()
		cursor.close()
		cursor.close()
		message = "Flights in next 30 days"
		createFlight = 'Successfully Created a New Flight'
		return render_template('view_flights.html', outBoundFlights = thirty_day_flights, message = message, createFlight = createFlight)


@app.route('/create_new_airplane', methods=['GET', 'POST'])
def create_new_airplane():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('create_new_airplane.html')

@app.route('/createNewAirplane', methods=['GET','POST'])
def createNewAirplane():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	airplane_ID = request.form['airplaneID']

	airplane_exists_query = 'SELECT * from airplane where airplaneID = %s and airline_name = %s'
	cursor.execute(airplane_exists_query, (airplane_ID, session['airline']))
	airplaneExists = cursor.fetchone()

	if(airplaneExists is not None):
		error = "This airplane already exists"
		cursor.close()
		return render_template('create_new_airplane.html', error = error)

	else:
		num_of_seats = request.form['num_of_seats']
		manufacturing_company = request.form['manufacturing_company']
		manufacturing_date = request.form['manufacturing_date']
		model_num = request.form['model_num']
		insert_airplane_query = 'INSERT INTO airplane VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(insert_airplane_query, (session['airline'], airplane_ID, num_of_seats, manufacturing_company, manufacturing_date, model_num))
		conn.commit();
		cursor.close()
		return redirect(url_for('view_airplanes'))

@app.route('/view_airplanes', methods=['GET', 'POST'])
def view_airplanes():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	cursor = conn.cursor()
	airplanes_query = 'SELECT * FROM airplane where airline_name = %s'
	cursor.execute(airplanes_query, (session['airline']))
	airplanes = cursor.fetchall();
	cursor.close()

	message = "Successfully Created New Airplane"

	return render_template('view_airplanes.html', airplanes = airplanes, message = message)


@app.route('/create_new_airport', methods=['GET', 'POST'])
def create_new_airport():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('create_new_airport.html')

@app.route('/createNewAirport', methods=['GET','POST'])
def createNewAirport():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	airport_code = request.form['code']
	airport_exists_query = 'SELECT * FROM airport where code = %s'
	cursor.execute(airport_exists_query, (airport_code))
	airportExists = cursor.fetchone()

	if(airportExists is not None):
		error = 'This airport code has already been used'
		cursor.close()
		return render_template('create_new_airport.html', error = error)
	else:
		airport_name = request.form['airport_name']
		airport_city = request.form['city']
		airport_country = request.form['country']
		airport_terminals = request.form['terminals']
		airport_type = request.form['airport_type']
		new_airport_insert = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s, %s)'

		cursor.execute(new_airport_insert, (airport_code, airport_name, airport_city, airport_city, airport_terminals, airport_type))
		conn.commit();
		cursor.close();
		error = 'Airport ' + airport_code + ' has Successfully been created'
		return render_template('create_new_airport.html', error = error)

@app.route('/search_flight_ratings', methods=['GET', 'POST'])
def search_flight_ratings():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('search_flight_ratings.html')


@app.route('/searchFlightRatings', methods=['GET', 'POST'])
def searchFlightRatings():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	airline_name = request.form['airline_name']
	flight_num = request.form['flight_num']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']

	flight_exists_query = 'SELECT * FROM flight where airline_name = %s and flight_num = %s and departure_time = %s and departure_date = %s'
	cursor.execute(flight_exists_query, (airline_name, flight_num, departure_time, departure_date))
	flightExists = cursor.fetchone()

	current_date = datetime.now().date()
	current_time = datetime.now().time()

	departure_date_nonString = datetime.strptime(departure_date, '%Y-%m-%d').date()
	departure_time_nonString = datetime.strptime(departure_time, '%H:%M').time()

	if(flightExists is None):
		error = 'This Flight does not exist'
		return render_template('search_flight_ratings.html', error = error)
	elif(departure_date_nonString > current_date and departure_time_nonString > current_time):
		error = 'This Flight has not happened yet and therefore has no reviews'
		return render_template('search_flight_ratings.html', error = error)

	return printFlightRatings(flightExists)


@app.route('/printFlightRatings', methods=['GET','POST'])
def printFlightRatings(flight):
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	reviews_query = 'SELECT * FROM review where ticketID in (SELECT ticketID FROM ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
	review_avg_query = 'SELECT avg(rate) as avgRate FROM review where ticketID in (SELECT ticketID FROM ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
	cursor.execute(reviews_query, (flight['airline_name'], flight['flight_num'], flight['departure_date'], flight['departure_time']))
	reviews = cursor.fetchall()
	cursor.execute(review_avg_query, (flight['airline_name'], flight['flight_num'], flight['departure_date'], flight['departure_time']))
	avgReview = cursor.fetchone()
	cursor.close()

	return render_template('print_flight_ratings.html', reviews = reviews, avgReview = avgReview, flight = flight)


@app.route('/view_reviews', methods=['GET'])
def view_reviews():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
	cursor.execute(flight_query, (request.args.get('param2'), request.args.get('param1'), request.args.get('param3'), request.args.get('param4')))
	flight = cursor.fetchone()
	cursor.close()

	return printFlightRatings(flight)


@app.route('/schedule_maintenance', methods=['GET', 'POST'])
def schedule_maintenance():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	return render_template('schedule_maintenance.html')


@app.route('/scheduleMaintenance', methods=['GET','POST'])
def scheduleMaintenance():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	airlineName = request.form['airline_name']
	airplaneID = request.form['airplane_ID']
	airplane_query = 'SELECT * FROM airplane WHERE airline_name = %s and airplaneID = %s'
	cursor.execute(airplane_query, (airlineName, airplaneID))
	airplane = cursor.fetchone()

	if(airplane is None):
		error = 'This Airplane does not Exist'
		cursor.close();
		return render_template('schedule_maintenance.html', error = error)
	
	flight_check_query = 'SELECT * from flight where assigned_airplaneID = %s and assigned_airplane_airline = %s'
	cursor.execute(flight_check_query, (airplaneID, airlineName))
	flights = cursor.fetchall()

	for flight in flights:
		arrival_date_NonStr = datetime.strptime(str(flight['arrival_date']), "%Y-%m-%d").date()
		departure_date_NonStr = datetime.strptime(str(flight['departure_date']), "%Y-%m-%d").date()
		arrival_time_NonStr = datetime.strptime(str(flight['arrival_time']), '%H:%M:%S').time()
		departure_time_nonStr = datetime.strptime(str(flight['departure_time']), '%H:%M:%S').time()

		#returns true if the maintancence and flight overlap
		st_date = request.form['start_date']
		end_date = request.form['end_date']
		st_time = str(request.form['start_time'])
		end_time = str(request.form['end_time'])
		maintenance_start_time = datetime.strptime(st_time, '%H:%M').time()
		maintenance_end_time = datetime.strptime(end_time, '%H:%M').time()
		maintenance_start_date = datetime.strptime(st_date, "%Y-%m-%d").date()
		maintenance_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

		if  (arrival_date_NonStr, arrival_time_NonStr) >= (maintenance_start_date, maintenance_start_time) and (departure_date_NonStr, departure_time_nonStr) <= (maintenance_end_date, maintenance_end_time):
			error = "Maintenance interferes with scheduled flight and therefore can not be created"
			cursor.close()
			return render_template('schedule_maintenance.html', error = error)

	maintenance_insert_query = 'INSERT INTO maintenance VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(maintenance_insert_query, (airlineName, airplaneID, request.form['start_date'], request.form['start_time'], request.form['end_date'], request.form['end_time']))
	conn.commit();
	cursor.close();
	message = 'Successfully scheduled maintenance for given airplane'
	return render_template('schedule_maintenance.html', message = message)

@app.route('/view_frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))
	
	cursor = conn.cursor()
	most_frequent_query = 'SELECT email_id, first_name, last_name, date_of_birth, count(*) as frequency from purchase natural join customer natural join ticket where airline_name = %s group by email_id order by frequency desc'
	cursor.execute(most_frequent_query, (session['airline']))
	customers = cursor.fetchall()
	cursor.close()
	return render_template('view_frequent_customers.html', customers = customers)

@app.route('/view_cusomter_flights', methods=['GET'])
def view_cusomter_flights():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor()
	user_email_id = request.args.get('param1')
	customer_query = 'SELECT * from customer where email_id = %s'
	cursor.execute(customer_query, (user_email_id))
	customer = cursor.fetchone()

	flights_query = 'SELECT airline_name, departure_airport, arrival_airport, assigned_airplane_airline, assigned_airplaneID, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price_ticket, flight_status, total_seats, available_seats from (customer, purchase) natural join ticket natural join flight where customer.email_id = purchase.email_id and customer.email_id = %s and airline_name = %s'
	cursor.execute(flights_query, (user_email_id, session['airline']))
	flights = cursor.fetchall();
	cursor.close()
	print(flights)
	for flight in flights:
		current_date = datetime.now().date()
		current_time = datetime.now().time()
		dep_time_string = str(flight['departure_time'])


		departure_time_nonString = datetime.strptime(dep_time_string, '%H:%M:%S').time()

		if(current_date > flight['departure_date']):
			flight['review'] = 'Reviews'
		elif(current_date == flight['departure_date'] and current_time >= departure_time_nonString):
			flight['review'] = 'Reviews'
		

	return render_template('view_customer_flights.html', customer = customer, flights = flights)

@app.route('/view_earned_revenue', methods=['GET', 'POST'])
def view_earned_revenue():
	if(isNotValidStaff()):
		return redirect(url_for('login_airline_staff'))

	cursor = conn.cursor();
	monthly_query = 'SELECT sum(amount_paid) as month_amt from purchase natural join ticket where airline_name = %s and purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)'
	cursor.execute(monthly_query, (session['airline']))
	monthly_amount = cursor.fetchone()

	yearly_query = 'SELECT sum(amount_paid) as year_amt from purchase natural join ticket where airline_name = %s and purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)'
	cursor.execute(yearly_query, (session['airline']))
	yearly_amount = cursor.fetchone()
	cursor.close()

	return render_template('view_earned_revenue.html', month = monthly_amount['month_amt'], year = yearly_amount['year_amt'])
##################################################




























################################################################################################################################



app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
