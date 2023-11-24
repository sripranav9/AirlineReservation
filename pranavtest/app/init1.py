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
def customer_login():
	return render_template('customer-login.html')

#Customer loginAuth and registerAuth, other related functions can be found in the CUSTOMER section below the "HOME - New Customer / Not logged in" section

#Define route for customer register
@app.route('/customer-register')
def customer_register():
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
            return redirect(url_for('customer_login'))
        except Exception as e:
            print(e)
            # Handle errors and rollback transaction
            conn.rollback()
            cursor.close()
            # Show an error message
            return render_template('customer-register.html', error="An error occurred during registration.")

@app.route('/loginAuth', methods=['GET', 'POST'])
def LoginAuth():
    #fetch login information from the form
    email = request.form['email']
    password = hashlib.md5(request.form['password'].encode()).hexdigest()
        
    #queries database to see if such tuple exists
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email_id = %s and pwd = %s'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
        
    error = None
    if(data):
        #if tuple exists create a session for the the user and login
        session['email'] = email
        session['password'] = password
        session['fname'] = data['first_name']
        session['lname'] = data['last_name']
        
        # If login is successful, check if the user was trying to make a purchase
        if session.pop('attempting_purchase', None):
            # Redirect to the purchase route if they were trying to buy something
            selected_outbound = session.pop('selected_outbound', None)
            selected_inbound = session.pop('selected_inbound', None)
            # return redirect(url_for('purchase'))
            return render_template('customer-purchase.html',
                                   selected_outbound=selected_outbound,
                                   selected_inbound=selected_inbound)
        else:
            # If not, redirect to the customer's home page
            return redirect(url_for('customerHome'))
    else:
        #if tuple doesn't exist then throw error message
        error = 'Invalid login or username'
        return render_template('customer-login.html', error=error)

def isNotValidCustomer():
	if(len(session) == 0): return True #no pair in session dictionary, so no session
	if(session['email'] is None): return True 
	if(session['password'] is None): return True
	email = session['email']
	password = session['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email_id = %s and pwd = %s'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	if(data is None): return True
	return False

@app.route('/customerHome', methods=['GET','POST'])
def customerHome():
        if(isNotValidCustomer()):
            return redirect(url_for('customer_login'))
        else:
            #if customer logs in after selecting flights
            if 'selected_outbound' in session or 'selected_inbound' in session:
                return redirect(url_for('purchase'))
            #session active - so pass the fname and other variables as necessary
            return render_template('customer-home.html', fname = session['fname'])

@app.route('/customer-logout')
def logout():
    session.clear()
    return redirect(url_for('customer_login'))

###
# @app.route('/customer-purchase', methods=['GET','POST'])
# def purchase():
#     if request.method == 'POST' and isNotValidCustomer():
#         #save the current session's flights to use after login
#         session['selected_outbound'] = request.form.get('selected_outbound')
#         session['selected_inbound'] = request.form.get('selected_inbound')
#         session['attempting_purchase'] = True #flag to check after login
#         #redirect customers to login since session is inactive

#         # DEBUGGING: Print the selected flights 
#         print("Selected Outbound Flight:", session['selected_outbound'])
#         print("Selected Inbound Flight:", session['selected_inbound'])

#         return redirect(url_for('customer_login'))
#     else: #request.method == 'POST':
#         # DEBUGGING: Print the selected flights 
#         print("Selected Outbound Flight:", request.form.get('selected_outbound'))
#         print("Selected Inbound Flight:", request.form.get('selected_inbound'))

#          # Customer is logged in and has selected flights to purchase
#         return render_template('customer-purchase.html',
#                                selected_outbound=session.get('selected_outbound'),
#                                selected_inbound=session.get('selected_inbound'))
#     # # If it's a GET request, just render the purchase page
#     # return render_template('customer-purchase.html')
###
@app.route('/customer-purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        if isNotValidCustomer():
            # Customer is not logged in but is trying to make a purchase
            session['selected_outbound'] = request.form.get('selected_outbound')
            session['selected_inbound'] = request.form.get('selected_inbound')
            # Set a flag to indicate a purchase attempt
            session['attempting_purchase'] = True
            # Redirect to login page
            return redirect(url_for('customer_login'))
        else:
            # Customer is logged in and has selected flights
            # Retrieve selected flights from the form or the session
            selected_outbound = request.form.get('selected_outbound') or session.get('selected_outbound')
            selected_inbound = request.form.get('selected_inbound') or session.get('selected_inbound')
            # Clear the flights from the session if they were stored
            session.pop('selected_outbound', None)
            session.pop('selected_inbound', None)
            # Render the purchase page with the selected flights
            return render_template('customer-purchase.html', 
                                   selected_outbound=selected_outbound,
                                   selected_inbound=selected_inbound)
    else:
        # GET request: Render the purchase page or redirect as needed
        # This is where you might redirect to the search page or handle accordingly
        return render_template('customer-purchase.html')

@app.route('/customer-purchase-confirmation', methods=['GET','POST'])
def purchase_confirmation():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))

    # Retrieve the session variables to confirm the purchase
    customer_email = session['email']
    selected_outbound = session.pop('selected_outbound', None)
    selected_inbound = session.pop('selected_inbound', None)

    # Process the form data from the customer-purchase page to confirm the purchase
    # For example, store the ticket details in the database

    # After processing, redirect to a page that confirms the purchase

    return render_template('customer-purchase-confirmation.html')


		
app.secret_key = 'some key that you will never guess'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
#Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
