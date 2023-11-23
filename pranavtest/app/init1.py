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
                       db='airline_reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

####################################################################
#HOME - New Customer / Not logged in

#Define a route for the index - home
@app.route('/')
def home():
	return render_template('index.html')

#Define route for customer login
@app.route('/customer-login')
def customerlogin():
	return render_template('customer-login.html')

#Customer loginAuth and registerAuth can be found in the CUSTOMER section below the "HOME - New Customer / Not logged in" section

#Define route for customer register
@app.route('/customer-register')
def customerregister():
	return render_template('customer-register.html')

@app.route('/search')
def search():
	return render_template('search.html')

@app.route('/searchresults', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        # Get data from form
        origin_code = request.form['origin']
        destination_code = request.form['destination']
        departure_date = request.form['departure_date']
        trip_type = request.form.get('trip') # Get the trip type (one-way or round-trip)
        return_date = request.form.get('return_date') if 'return_date' in request.form else None


        # SQL Query the database
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s',
            (origin_code, destination_code, departure_date)
        )
        outbound_flights = cursor.fetchall()

        #Initialise an empty list for inbound flights
        # If round-trip, query the database for inbound flights
        if trip_type == 'round-trip' and return_date:
            cursor.execute(
                'SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s',
                (destination_code, origin_code, return_date)
            )
        inbound_flights = cursor.fetchall()

        cursor.close()

        # Render the results in a HTML table
        return render_template('searchresults.html', outbound_flights=outbound_flights, inbound_flights=inbound_flights, trip_type=trip_type)
    
    # If method is GET, just render the search form
    return render_template('search.html')
####################################################################

####################################################################
# CUSTOMER

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    customer_email = request.form['emailid']
    cursor = conn.cursor()

    # Check if email already exists
    query = 'SELECT * FROM customer WHERE email_id = %s'
    cursor.execute(query, (customer_email))
    emailExists = cursor.fetchone()

    error = None #declaring a variable maybe?
    if (emailExists): 
        #the emailExists variable has data - same email found in the database
        return render_template('customer-register.html', error = "This user already exists in the database. Try Logging in")
        
    else:
        #good to be added
        customer_password = hashlib.md5(request.form['password'].encode()).hexdigest()
        first_name = request.form['fname']
        last_name = request.form['lname']
        date_of_birth = request.form['date-of-birth']
        building_num = request.form['building-num']
        street_name = request.form['street-name']
        apt_num = request.form['apt-num']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip-code']
        passport_num = request.form['passport-number']
        passport_country = request.form['passport-country']
        passport_expiry = request.form['passport-expiry']
        insert_newcustomer_query = 'INSERT INTO customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        try:
            cursor.execute(insert_newcustomer_query, (
                customer_email, first_name, last_name, customer_password, 
                building_num, street_name, apt_num, city, state, zip_code, 
                passport_num, passport_country, passport_expiry, date_of_birth,
            ))
            phone_numbers = request.form.getlist('customer_phone[]')
            insert_phone_query = 'INSERT INTO customer_phone VALUES(%s, %s)'
            phone_already_query = 'SELECT * from customer_phone where email_id = %s and phone_num = %s'
            for phone in phone_numbers:
                if(phone == ''): continue
                cursor.execute(phone_already_query, (customer_email, phone))
                phoneExists = cursor.fetchone();
                if(phoneExists is None):
                    cursor.execute(insert_phone_query, (customer_email, phone))
            conn.commit()
            cursor.close()
            # Redirect to login page after registration
            return redirect(url_for('customer-login'))
        except Exception as e:
            print(e)
            # Handle errors and rollback transaction
            conn.rollback()
            cursor.close()
            # Show an error message
            return render_template('customer-register.html', error="An error occurred during registration.")

		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)