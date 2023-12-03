#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import uuid
import random

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

# Customer loginAuth and registerAuth, other related functions can be found in the CUSTOMER section below the "HOME - New Customer / Not logged in" section

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
            # Query for fetching all the details from flight table
            # cursor.execute(
            #     'SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s',
            #     (origin_code, destination_code, departure_date)
            # )
        # Query for fetching all the details + dynamic price from flight table
        cursor.execute('''
        SELECT *,
        CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
        FROM flight
        WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s 
        AND available_seats > 0 AND flight_status != 'canceled'
		''', (origin_code, destination_code, departure_date))
        outbound_flights = cursor.fetchall()

        # If round-trip, query the database for inbound flights
        if trip_type == 'round-trip' and return_date:
                # Query for fetching all the details from flight table
                # cursor.execute(
                #     'SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s',
                #     (destination_code, origin_code, return_date)
                # )
            # Query for fetching all the details + dynamic price from flight table
            cursor.execute('''
                SELECT *,
                CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL (10,2)) AS dynamic_price
                FROM flight
                WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s
                AND available_seats > 0 AND flight_status != 'canceled'
                ''', (destination_code, origin_code, return_date))
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

    if (emailExists): 
        # The emailExists variable has data - same email found in the database
        return render_template('customer-register.html', error = "This user already exists in the database. Try Logging in")
        
    else:
        # Verified as a new user - email not found
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
        # If tuple exists - create a session for the the user and login
        session['email'] = email
        session['password'] = password
        session['fname'] = data['first_name']
        session['lname'] = data['last_name']
        session['dob'] = data['date_of_birth']
        
        # If login is successful, check if the user was trying to make a purchase
        if session.pop('attempting_purchase', None):
            # Redirect to the purchase route if they were trying to buy something
            selected_outbound = session.get('selected_outbound')
            selected_inbound = session.get('selected_inbound')
            total_cost = session.get('total_cost')
            # return redirect(url_for('purchase'))
            ######
            # Since I want the flight details in a table, I need to execute those queries again here.
            # Copy Pasted from the customer-purchase function
            cursor = conn.cursor()
            details_selected_outbound = None
            details_selected_inbound = None # This is to ensure a successful build and run, since inbound is not always present
            
            outbound_details = selected_outbound.split('_')
        
            details_selected_outbound_query = '''
            SELECT *,
            CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
            FROM flight
            WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
            AND available_seats > 0 AND flight_status != 'canceled'
            '''
            cursor.execute(details_selected_outbound_query, (outbound_details[1], 
                                                 outbound_details[0], outbound_details[2], outbound_details[3]))
            details_selected_outbound = cursor.fetchall() # To be passed on to the HTML to display
            
            if selected_inbound:
                inbound_details = selected_inbound.split('_')
                details_selected_inbound_query = '''
                SELECT *,
                CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
                FROM flight
                WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
                AND available_seats > 0 AND flight_status != 'canceled'
                '''
                cursor.execute(details_selected_inbound_query, (inbound_details[1], 
                                                    inbound_details[0], inbound_details[2], inbound_details[3]))            
                details_selected_inbound = cursor.fetchall() # To be passed on to the HTML to display
            
            cursor.close()
            # Paste from the Customer Purchase ends
            ######
            return render_template('customer-purchase.html',
                                   selected_outbound=selected_outbound,
                                   selected_inbound=selected_inbound, total_cost=total_cost,
                                   details_selected_outbound=details_selected_outbound,
                                  details_selected_inbound=details_selected_inbound)
        else:
            # If not, redirect to the customer's home page
            return redirect(url_for('customerHome'))
    else:
        # Throw an error message if the tuple does not exist
        error = 'Invalid login or username'
        return render_template('customer-login.html', error=error)

def isNotValidCustomer():
	if(len(session) == 0): return True # No pair in session dictionary i.e. no session created yet
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
            # If customer logs in after selecting flights
            if 'selected_outbound' in session or 'selected_inbound' in session:
                # return redirect(url_for('purchase'))
                return render_template('customer-home.html', fname = session['fname'])
            #session active - so pass the fname and other variables as necessary
            return render_template('customer-home.html', fname = session['fname'])

@app.route('/customer-logout')
def logout():
    # Clear all the session data
    session.clear()
    return redirect(url_for('customer_login'))

@app.route('/customer-purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        if isNotValidCustomer():
            # Customer is not logged in but is trying to make a purchase
            session['selected_outbound'] = request.form.get('selected_outbound')
            session['selected_inbound'] = request.form.get('selected_inbound')
            session['total_cost'] = request.form['total_cost'] 
            session['outbound_cost'] = request.form['outbound_cost'] 
            session['inbound_cost'] = request.form['inbound_cost'] 
            # print(session['outbound_cost'], session['inbound_cost'], session['total_cost']) # Debugging purpose
            # Set a flag to indicate a purchase attempt
            session['attempting_purchase'] = True
            # Redirect to login page
            return redirect(url_for('customer_login'))
        else:
            # Customer is logged in and has selected flights

            # Missing these 2 lines made me spend 2 days. Flagging this to cherish my debugging skills later
            # Retrieve selected flights from the form or the session
            session['selected_outbound'] = request.form.get('selected_outbound')
            session['selected_inbound'] = request.form.get('selected_inbound')
            ##
            session['total_cost'] = request.form['total_cost'] 
            session['outbound_cost'] = request.form['outbound_cost'] 
            session['inbound_cost'] = request.form['inbound_cost'] 
            # print(session['outbound_cost'], session['inbound_cost'], session['total_cost']) # Debugging purpose

            selected_outbound = request.form.get('selected_outbound') or session.get('selected_outbound')
            selected_inbound = request.form.get('selected_inbound') or session.get('selected_inbound')
            total_cost = request.form.get('total_cost') or session.get('total_cost')

            cursor = conn.cursor()
            details_selected_outbound = None
            details_selected_inbound = None # This is to ensure a successful build and run, since inbound is not always present
            
            # Format: EK201_Emirates_2023-11-07_15:00:00
            outbound_details = selected_outbound.split('_')
        
            details_selected_outbound_query = '''
            SELECT *,
            CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
            FROM flight
            WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
            AND available_seats > 0 AND flight_status != 'canceled'
            '''
            cursor.execute(details_selected_outbound_query, (outbound_details[1], 
                                                 outbound_details[0], outbound_details[2], outbound_details[3]))
            details_selected_outbound = cursor.fetchall() # To be passed on to the HTML to display
            
            if selected_inbound:
                inbound_details = selected_inbound.split('_')
                details_selected_inbound_query = '''
                SELECT *,
                CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
                FROM flight
                WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
                AND available_seats > 0 AND flight_status != 'canceled'
                '''
                cursor.execute(details_selected_inbound_query, (inbound_details[1], 
                                                    inbound_details[0], inbound_details[2], inbound_details[3]))            
                details_selected_inbound = cursor.fetchall() # To be passed on to the HTML to display

            
            # Clear the flights from the session if they were stored
            # session.pop('selected_outbound', None)
            # session.pop('selected_inbound', None)
            # session.pop('total_cost', None)
            # Commented because - using these in customer-purchase-confirmation
            
            cursor.close()
            # Render the purchase page with the selected flights
            return render_template('customer-purchase.html', 
                                   selected_outbound=selected_outbound,
                                   selected_inbound=selected_inbound, total_cost=total_cost,
                                   details_selected_inbound=details_selected_inbound,
                                   details_selected_outbound=details_selected_outbound)
    else:
        return render_template('customer-purchase.html')


def generate_ticket_id(cursor):
    max_int = 2147483647  # Maximum value for a signed 4-byte integer
    while True:
        # Generate a random ticket ID
        ticket_id = random.randint(1, max_int)
        cursor.execute('SELECT ticketID FROM ticket WHERE ticketID = %s', (ticket_id))
        result = cursor.fetchone()
        if result is None:
            return ticket_id

@app.route('/customer-purchase-confirmation', methods=['GET','POST'])
def purchase_confirmation():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))

    # Retrieve the session variables to confirm the purchase
    customer_email = session['email']
    customer_fname = session['fname'], 
    customer_lname = session['lname'], 
    # customer_dob = session['dob'] having an error with the date format
    selected_outbound = session.pop('selected_outbound', None)
    # selected_outbound = session.get('selected_outbound')
    selected_inbound = session.pop('selected_inbound', None)
    # selected_inbound = session.get('selected_inbound')

    # Remember the total cost calculated by JavaScript in searchresults.html
    total_cost = session.get('total_cost')
    outbound_cost = session.get('outbound_cost')
    inbound_cost = session.get('inbound_cost')

    print(selected_inbound, selected_outbound)
    # total_cost = session.pop('total_cost', None)

    # Process the form data from the customer-purchase page to confirm the purchase
    card_type = request.form['card_type']
    card_number = request.form['card_number']
    name_on_card = request.form['name_on_card']
    expiration_date = request.form['expiration_date']

    # Generate a unique ticketID
    cursor = conn.cursor()
    outboundTicketID = generate_ticket_id(cursor)
    inboundTicketID = generate_ticket_id(cursor) if selected_inbound else None

    # Add tuples to ticket, purchase & Update flight
    try:
        if selected_outbound:
            # Add data to ticket table: Insert into ticket table first due to the foreign key references from Purchase to Ticket
            outbound_details = selected_outbound.split('_') # Split the concatenated data from HTML/JS
            ticket_insert_query = '''
            INSERT INTO ticket (ticketID, airline_name, flight_num, departure_date, departure_time)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(ticket_insert_query, (outboundTicketID, outbound_details[1], outbound_details[0], outbound_details[2], outbound_details[3]))

            # Add data to purchase table
            purchase_insert_query = '''
            INSERT INTO purchase (ticketID, email_id, first_name, last_name, date_of_birth, card_type, card_num, name_on_card, expiration_date, purchase_date, purchase_time, amount_paid)
            SELECT %s, %s, first_name, last_name, date_of_birth, %s, %s, %s, %s, CURDATE(), CURTIME(), %s
            FROM customer WHERE email_id = %s
            '''
            cursor.execute(purchase_insert_query, 
                (outboundTicketID, 
                    customer_email, 
                    card_type, 
                    card_number, 
                    name_on_card, 
                    expiration_date,
                    outbound_cost, 
                    customer_email))
            
            # Update available seats on flight table
            update_seats_query = 'UPDATE flight SET available_seats = available_seats - 1 WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s'
            cursor.execute(update_seats_query, (outbound_details[1], outbound_details[0], outbound_details[2], outbound_details[3]))
            
        if selected_inbound:
            # Add data to ticket table
            inbound_details = selected_inbound.split('_')
            ticket_insert_query = '''
            INSERT INTO ticket (ticketID, airline_name, flight_num, departure_date, departure_time)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(ticket_insert_query, (inboundTicketID, inbound_details[1], inbound_details[0], inbound_details[2], inbound_details[3]))

            # Add data to purchase table
            purchase_insert_query_return = '''
            INSERT INTO purchase (ticketID, email_id, first_name, last_name, date_of_birth, card_type, card_num, name_on_card, expiration_date, purchase_date, purchase_time, amount_paid)
            SELECT %s, %s, first_name, last_name, date_of_birth, %s, %s, %s, %s, CURDATE(), CURTIME(), %s
            FROM customer WHERE email_id = %s
            '''
            cursor.execute(purchase_insert_query_return, 
                (inboundTicketID, 
                    customer_email, 
                    card_type, 
                    card_number, 
                    name_on_card, 
                    expiration_date,
                    inbound_cost, 
                    customer_email))        

            # Update available seats on flight table
            update_seats_query = 'UPDATE flight SET available_seats = available_seats - 1 WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s'
            cursor.execute(update_seats_query, (inbound_details[1], inbound_details[0], inbound_details[2], inbound_details[3]))

        # Commit the changes to the database
        conn.commit()

    except Exception as e:
         print('Could not proceed with purchase transaction. Aborting.')
         print(e)
         conn.rollback()
         error = "Could not complete the transaction. Aborted."
         return render_template('customer-purchase.html', error=error)

    finally:
        # Ensure cursor is closed regardless
        cursor.close()

    # After processing, redirect to a page that confirms the purchase
    return render_template('customer-purchase-confirmation.html', outboundTicketID=outboundTicketID, inboundTicketID=inboundTicketID)

# @app.route('/customer-spending', methods=['GET','POST'])
# def customer_spending():
#     if(isNotValidCustomer()):
#         # The user is not logged in, redirect them to the login page
#         return redirect(url_for('customer_login'))
    
#     customer_email = session['email'] # To load the customer data accordingly
#     cursor = conn.cursor()

#     # Query to get the Purchase History and connected Ticket data
#     spending_history_query = '''
#             SELECT p.ticketID, p.amount_paid, p.purchase_date, p.purchase_time, 
#             t.airline_name, t.flight_num ,t.departure_date, t.departure_time 
#             FROM `purchase` as p ,`ticket` as t 
#             WHERE t.ticketID = p.ticketID AND p.email_id = %s
#             ORDER BY purchase_date DESC, purchase_time DESC;
#             '''
#     cursor.execute(spending_history_query, (customer_email))
#     spending_history_data = cursor.fetchall()

#     # Query to get the total amount spent by the customer in session
#     total_spent_query = 'SELECT SUM(amount_paid) AS total_amount FROM `purchase` WHERE email_id = %s'
#     cursor.execute(total_spent_query, (customer_email))
#     total_spent_amount = cursor.fetchone()

#     cursor.close()
    
#     return render_template('customer-spending.html', spending_history_data=spending_history_data,
#                            total_spent_amount=total_spent_amount['total_amount'] )

@app.route('/customer-spending', methods=['GET','POST'])
def customer_spending():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))
    
    customer_email = session['email'] # To load the customer data accordingly
    cursor = conn.cursor()

    # Query to get the total amount spent by the customer in the past year
    total_spent_past_year_query = '''
        SELECT SUM(amount_paid) AS total_amount
        FROM `purchase`
        WHERE email_id = %s AND purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()
    '''
    cursor.execute(total_spent_past_year_query, (customer_email,))
    total_spent_past_year = cursor.fetchone()

    # Query to get the month-wise spending for the last six months
    monthly_spending_query = '''
        SELECT MONTHNAME(purchase_date) AS month, YEAR(purchase_date) AS year, 
            SUM(amount_paid) AS total_amount 
        FROM purchase 
        WHERE email_id = %s AND 
            purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 MONTH) AND 
            CURDATE() GROUP BY month, year 
        ORDER BY year, month DESC;
    '''
    cursor.execute(monthly_spending_query, (customer_email))
    monthly_spending_data = cursor.fetchall()

    cursor.close()
    
    return render_template('customer-spending.html', spending_history_data=spending_history_data,
                           total_spent_amount=total_spent_amount['total_amount'] )

@app.route('/customer-rate-flight', methods=['GET'])
def customer_rate_flight():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))
    
    customer_email = session.get('email')  # Retrieve the logged-in user's email from the session
    cursor = conn.cursor()

    # Fetch flights that have not been rated by the user yet: Display details from flight and purchase, and check the review table for existing entries
    query = '''
    SELECT 
        p.ticketID,
        f.airline_name, 
        f.flight_num, 
        f.departure_airport,
        f.arrival_airport,
        f.departure_date, 
        f.departure_time
    FROM 
        purchase p, flight f, ticket t
    WHERE 
        p.ticketID = t.ticketID AND
        t.airline_name = f.airline_name AND
        t.flight_num = f.flight_num AND
        t.departure_date = f.departure_date AND
        t.departure_time = f.departure_time AND
        p.email_id = %s AND 
        (f.arrival_date < CURRENT_DATE() OR (f.arrival_date = CURRENT_DATE() AND f.arrival_time < CURRENT_TIME())) AND
        NOT EXISTS (
            SELECT 1 FROM review r WHERE r.ticketID = p.ticketID
        )
    '''
    cursor.execute(query, (customer_email))
    flights_to_rate = cursor.fetchall()
    cursor.close()

    return render_template('customer-rate-flight.html', flights=flights_to_rate)

@app.route('/customer-submit-rating', methods=['POST'])
def customer_submit_rating():
    # Retrieve data from form
    ticketID = request.form.get('ticketID')
    rate = request.form.get('rate')
    comment = request.form.get('comment')
    customer_email = session.get('email')  # Assume user is logged in and email is in session

    cursor = conn.cursor()
    query = 'INSERT INTO review (ticketID, email_id, rate, comment) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (ticketID, customer_email, rate, comment))
    conn.commit()  # Don't forget to commit your changes
    cursor.close()

    return redirect(url_for('customer_rate_flight'))

@app.route('/customer-view-flights', methods=['GET','POST'])
def customer_view_flights():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))

    customer_email = session.get('email')  # Retrieve the logged-in user's email from the session
    cursor = conn.cursor()

    # Fetch upcoming flights
    upcoming_flights_query = '''
        SELECT p.ticketID, f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
        f.departure_date, f.departure_time,
        (f.departure_date > CURRENT_DATE() OR 
        (f.departure_date = CURRENT_DATE() AND f.departure_time > ADDTIME(CURRENT_TIME(), '24:00:00'))) AS can_cancel
        FROM purchase p, flight f, ticket t WHERE p.ticketID = t.ticketID AND 
        t.airline_name = f.airline_name AND
        t.flight_num = f.flight_num AND
        t.departure_date = f.departure_date AND
        t.departure_time = f.departure_time AND
        p.email_id = %s
        AND f.departure_date >= CURRENT_DATE()
        ORDER BY departure_date ASC, departure_time ASC
    '''
    # The above SQL Query has a boolean value that shows whether the flight is less than 24 hours away, by which the user cannot be provided an option to cancel
    cursor.execute(upcoming_flights_query, (customer_email,))
    upcoming_flights = cursor.fetchall()

     # Fetch previous flights
    previous_flights_query = '''
        SELECT p.ticketID, f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
        f.departure_date, f.departure_time
        FROM purchase p, flight f, ticket t WHERE p.ticketID = t.ticketID AND 
        t.airline_name = f.airline_name AND
        t.flight_num = f.flight_num AND
        t.departure_date = f.departure_date AND
        t.departure_time = f.departure_time AND
        p.email_id = %s
        AND f.departure_date < CURRENT_DATE()
        ORDER BY departure_date DESC, departure_time DESC
    '''
    cursor.execute(previous_flights_query, (customer_email))
    previous_flights = cursor.fetchall()

    cursor.close()

    return render_template('customer-view-flights.html', upcoming_flights = upcoming_flights, previous_flights = previous_flights)

@app.route('/customer-cancel-flight', methods=['GET','POST'])
def customer_cancel_flight():
    if(isNotValidCustomer()):
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('customer_login'))
    
    # Get the ticketID from customer view flights page
    ticket_id_to_cancel = request.form.get('cancel_ticket_id')
    customer_email = session['email']

    cursor = conn.cursor()

    # Check if the flight is more than 24 hours away
    # (Double checking in the back-end too. Already blocked in the front-end)
    query = '''
    SELECT
        (f.departure_date > CURRENT_DATE() OR 
        (f.departure_date = CURRENT_DATE() AND f.departure_time > ADDTIME(CURRENT_TIME(), '24:00:00'))) AS can_cancel
        FROM purchase p, flight f, ticket t WHERE p.ticketID = t.ticketID AND 
        t.airline_name = f.airline_name AND
        t.flight_num = f.flight_num AND
        t.departure_date = f.departure_date AND
        t.departure_time = f.departure_time AND
        p.ticketID = %s AND p.email_id = %s
        AND f.departure_date >= CURRENT_DATE()
    '''
    cursor.execute(query, (ticket_id_to_cancel, customer_email))
    can_cancel = cursor.fetchone()
    
    if can_cancel and (can_cancel['can_cancel'] == 1):
        try:
            # Add 1 available_seat to the flight
            update_seats_query = '''
            UPDATE flight f
                JOIN ticket t ON f.airline_name = t.airline_name 
                AND f.flight_num = t.flight_num 
                AND f.departure_date = t.departure_date 
                AND f.departure_time = t.departure_time
            SET f.available_seats = f.available_seats + 1
            WHERE t.ticketID = %s;
            '''
            cursor.execute(update_seats_query, (ticket_id_to_cancel))
            
            # Delete the data from purchase and ticket table in the same order
            cursor.execute('DELETE FROM purchase WHERE ticketID = %s AND email_id = %s', (ticket_id_to_cancel, customer_email))
            cursor.execute('DELETE FROM ticket WHERE ticketID = %s', (ticket_id_to_cancel))
            conn.commit()

        except Exception as e:
            conn.rollback()  # Roll back the transaction on error
            print(f"Error: {e}")  # Logging the exception can help in debugging
            error = "Could not complete the cancellation. Aborted."
            return render_template('customer-view-flights.html', error=error)
        
        finally:
            cursor.close()  # Ensure the cursor is closed
    else:
        cursor.close()  # Close cursor if cancellation is not allowed
        error = "Flight cannot be cancelled within 24 hours of departure."
        return render_template('customer-view-flights.html', error=error)

    return redirect(url_for('customer_view_flights'))

app.secret_key = 'some key that you will never guess'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
#Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
