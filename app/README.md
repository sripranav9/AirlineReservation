# Airline Ticket Reservation System
### Course Project - Database Design and Web Application Development
CS-UY 3083 Introduction to Databases <br/>
NYU Tandon School of Enginnering <br/>
Professor Ratan Dey <br/>
Fall 2023 <br/>

## Introduction
Air Ticket Reservation System is a project undertaken for the Intro to Databases course (CS-UY 3083) at New York University, Tandon School of Engineering, guided by Professor Ratan Dey during the Fall 2023 semester. This project is meant to provide a hands-on experience in developing a relational database and a backend-driven web application.

Our system is centered around providing a functional and efficient platform for air ticket reservation, primarily focusing on backend database implementation. The project serves two main user groups: Customers and Airline Staff. While Customers have the ability to search for flights, book tickets, and manage their reservations, Airline Staff are enabled to handle flight details, update statuses, and manage customer interactions.

It's important to note that this project emphasizes backend functionality over frontend aesthetics. As such, the application is not extensively styled with CSS or other frontend technologies, as the primary objective is to demonstrate robust backend capabilities and effective database integration.

## Features
Key features include:
- Functional interfaces for flight searches, ticket bookings, and user management.
- Dedicated login and registration modules for enhanced security.
- Comprehensive access to flight information for customers, including past, current, and future flights.
- Extensive flight management options for airline staff, encompassing flight creation, status updates, and customer service.
- Saved flight selections for users not logged in, and many more!

### Group Members/ Contributers:
[Sri Pranav Srivatsavai](mailto:sri.pranav@nyu.edu) | [Theo Welckle](mailto:tlw9927@nyu.edu)

<a href="https://github.com/sripranav9/AirlineReservation/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=sripranav9/AirlineReservation" />
</a>


## Setup and Installation
### Prerequisites
- [XAMPP](https://www.apachefriends.org/index.html) for SQL database management.
- [Python](https://www.python.org/downloads/) (version 3.x is recommended).
- [pip](https://pip.pypa.io/en/stable/installing/) for Python package management.

### XAMPP and SQL Setup
1. Download and install XAMPP from the official website.
2. Open XAMPP Control Panel and start Apache and MySQL modules.
3. Create a new SQL database for the project via `http://localhost/phpmyadmin`.

### Flask Environment Setup
1. Install Flask using pip:
   ```bash
   pip install Flask
   ```
2. (Optional) Create a virtual environment to isolate your Python packages for this project:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. If you have a requirements.txt file for your project (listing all the necessary Python packages), install them using:
   ```bash
   pip install -r requirements.txt
   ```
### Flask Environment Setup
1. Navigate to your Flask application directory.
2. If you are not using a virtual environment:

   a. Copy the path of your file and paste it on terminal following the command:
   ```bash
   python /Users/sripranav/Documents/GitHub/AirlineReservation/app/init1.py # Just an example: Copy and paste the file location directly
   ```
4. If you are using a virtual environemnt:

   a. Set environment variables to specify the Flask application and environment. Replace your-app.py with the name of your main Python file:
     ```bash
     export FLASK_APP=your-app.py  # On Windows, use `set FLASK_APP=your-app.py`
     export FLASK_ENV=development  # This enables debug mode
     ```
   b. Run the flask application:
     ```bash
     flask run
     ```

## Use Cases
Here, list all the use cases of your application. For each use case, provide a brief description.



### 1. Public (No Users Logged In)
The following are the use cases for when no user is logged in.
#### i. View Public Information
- Description: Check flight status and search for future flights
- SQL Queries:
  - Query 1: Fetch details from `flight` and show a dynamic price based on the available seats.
    ```python
    cursor.execute('''
        SELECT *,
        CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
        FROM flight
        WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s 
        AND available_seats > 0 AND flight_status != 'canceled'
		''', (origin_code, destination_code, departure_date))
    ```
    *Explanation: The query fetches all the required details from the `flight` table by checking for flights that are not cancelled and have atleast 1 available seat. The dynamic pricing follows the strategy where the ticket will cost 25% more than the base price if the flight capacity is above 80%. Then customer is then taken to the purchase page to continue. The same query is used to display the return flights as well.*

  - The web application will route the customer to a customer login page if the user tries to purchase a ticket without logging in. The flight selection will be saved for the customer's purchase view after log in is authenticated.

  - Query 2: Fetch the flight status based on the details from the form.
    ```python
    #paste the sql query from the flask app here
    ```

#### ii. checkFlightStatus()
- **Description**: Function is used for anybody to check the status of a flight based on certain criteria they must fill out in a form
- **SQL Queries**:
  - Query 1: Queries the database to retrieve the flight the general user wants to check the status of
    ```python
    flight_query = 'SELECT * FROM flight where airline_name = %s and flight_num = %s and departure_date = %s and arrival_date = %s'
    ```


#### iii. Login and Register
- **Description and SQL Queries**: The login and register modules for [customers](#2-customer) and [airline staff](#3-airline-staff) will be explained in the respective use case groups.



### 2. Customer
The following are the use cases for when a customer's login is authenticated.

#### i. Register
- **Description**: The customer will be able to create a new account by opting to register. The username and password provided will be used for logging in, and the password is saved in an **md5 hash format** in the database.
- **SQL Queries**:
  - Query 1: Check if the email already exists and throw an error if it does.
    ```python
    query = 'SELECT * FROM customer WHERE email_id = %s'
    # ...
    return render_template('customer-register.html', error = "This user already exists in the database. Try Logging in")
    ```
    *Explanation: If the user already exists, throw an error. Otherwise, proceed to process the other fields of the register form received.*

  - Query 2: Insert the values from the form into the respective tables in the database.
    ```python
    # ...
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
    # ...
    ```
    *Explanation: The queries above are responsible for inserting the values from the form into the `customer` and `customer_phone` table, and only adds a phone number after checking for duplicates. The flask application uses the try, except, and finally methods to add data to enhance the efficiency of the transaction.*

#### ii. Login
- **Description**: The customer will be able to login to the system if they provide the correct login details, else will be presented with an error.
- **SQL Queries**:
  - Query 1: Check for the tuple's existence in the `customer` table to verify the details.
    ```python
    # ...
    password = hashlib.md5(request.form['password'].encode()).hexdigest()
    query = 'SELECT * FROM customer WHERE email_id = %s and pwd = %s'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    if(data):
        # If tuple exists - create a session for the the user and login
    else:
      error = 'Invalid login or username'
      return render_template('customer-login.html', error=error)
    # ...
    ```
    *Explanation: Convert the password from the form into an **md5 hash** and fetch details from the `customer` table and begin a session while redirecting them to the Customer Home page. Also, handle the errors if the tuple does not exist.*

  - Query 2: Function to check valid customer login before every function.
    ```python
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
    ```
    *Explanation: This function will be called in all the customer use cases to ensure legit access and implementation of the functions.*

#### iii. Logout
- **Description**: Log out the user by deleting all the session data and displaying the login page.
- **SQL Queries**:
  - This function does not need any SQL queries.
    ```python
    session.clear()
    return redirect(url_for('customer_login'))
    ```
    *Explanation: The session data is deleted so that there are no conflicts when a new user logs in.*

#### iv. View my Flights
- **Description**: Fetch the upcoming flights and previous flights of the customer. Provide an option to cancel the flight if the scheduled departure is more than 24 hours (discussed in the 'Cancel Ticket' use case).
- **SQL Queries**:
  - Query 1: Fetch the upcoming flight details from `flight`, `purchase`, and `ticket` and order in descending order of departure date and time.
    ```python
    upcoming_flights_query = '''
        SELECT p.first_name, p.ticketID, f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
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
    ```
    *Explanation: The query checks for the system's current date and time to differentiate upcoming and previous flights. It fetches the details necessary for the customer to understand which flight they are looking at. There is an additional `can_cancel` attribute that decides whether there is more than 24 hours for the scheduled departure.*

  - Query 2: Fetch the previous flight details from `flight`, `purchase`, and `ticket` and order in ascending order of departure date and time.
    ```python
    previous_flights_query = '''
        SELECT p.first_name, p.ticketID, f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
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
    ```
    *Explanation: The query checks for the system's current date and time to differentiate upcoming and previous flights. It fetches the details necessary for the customer to understand which flight they are looking at.*

#### v. Search for Flights
- **Description**: The customer will be able to search for flights, similar to the use case mentioned in the [Public](#1-public-no-users-logged-in) section.
- **SQL Queries**:
  - Query 1: Fetch details from `flight` and show a dynamic price based on the available seats.
    ```python
    cursor.execute('''
        SELECT *,
        CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
        FROM flight
        WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s 
        AND available_seats > 0 AND flight_status != 'canceled'
		''', (origin_code, destination_code, departure_date))
    ```
    *Explanation: The query fetches all the required details from the `flight` table by checking for flights that are not cancelled and have atleast 1 available seat. The dynamic pricing follows the strategy where the ticket will cost 25% more than the base price if the flight capacity is above 80%. Then customer is then taken to the purchase page to continue. The same query is used to display the return flights as well.*

#### vi. Purchase Tickets
- **Description**: The customer will be able to purchase a ticket for himself or other people (1 ticket at once) for the flights that have atleast 1 available seat, and are not having a canceled status.
- **SQL Queries**:
  - Query 1: Display the selection of flights: Outbound and Inbound (if a round-trip is selected).
    ```python
    details_selected_outbound_query = '''
            SELECT *,
            CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
            FROM flight
            WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
            AND available_seats > 0 AND flight_status != 'canceled'
            '''
    if selected_inbound:
                inbound_details = selected_inbound.split('_')
                details_selected_inbound_query = '''
                SELECT *,
                CAST(base_price_ticket * IF(((total_seats - available_seats) / total_seats) >= 0.8, 1.25, 1) AS DECIMAL(10,2)) AS dynamic_price
                FROM flight
                WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s
                AND available_seats > 0 AND flight_status != 'canceled'
                '''
    ```
    *Explanation: The queries above are quite similar to the ones used for the search flights function. This is meant to give user a chance to see their final flight selection and confirm to continue to the payment method.*
    
  - Generate a unique TicketID
    ```python
    def generate_ticket_id(cursor):
    max_int = 2147483647  # Maximum value for a signed 4-byte integer
    while True:
        # Generate a random ticket ID
        ticket_id = random.randint(1, max_int)
        cursor.execute('SELECT ticketID FROM ticket WHERE ticketID = %s', (ticket_id))
        result = cursor.fetchone()
        if result is None:
            return ticket_id
    ```
    *Explanation: This function generates a ticket ID for each leg of the flight: checks for an existing ticket ID with the same randomly generated ID before returning the generated value. If there is a same ID number existing, the function will generate a new ticket ID.*

  - Query 2: Add the customer data into tables `ticket` and `purchase`. Update the `flight` table.
    ```python
    # Add data to ticket table: Insert into ticket table first due to the foreign key references from Purchase to Ticket
    
    # Insert into ticket table
    ticket_insert_query = '''
            INSERT INTO ticket (ticketID, airline_name, flight_num, departure_date, departure_time)
            VALUES (%s, %s, %s, %s, %s)
            '''

    # Insert into purchase table: Check if the ticket is for the customer or someone else
    if buying_for_others:
        # Customer buying a ticket for someone else
        purchase_insert_query = '''
        INSERT INTO purchase (ticketID, email_id, first_name, last_name, date_of_birth, card_type, card_num, name_on_card, expiration_date, purchase_date, purchase_time, amount_paid)
        SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), CURTIME(), %s
        FROM customer WHERE email_id = %s
        '''
    else:
        # Customer buying a ticket for himself - Add data to purchase table
        purchase_insert_query = '''
        INSERT INTO purchase (ticketID, email_id, first_name, last_name, date_of_birth, card_type, card_num, name_on_card, expiration_date, purchase_date, purchase_time, amount_paid)
        SELECT %s, %s, first_name, last_name, date_of_birth, %s, %s, %s, %s, CURDATE(), CURTIME(), %s
        FROM customer WHERE email_id = %s
        '''
    
    # Update available seats on flight table
    update_seats_query = 'UPDATE flight SET available_seats = available_seats - 1 WHERE airline_name = %s AND flight_num = %s AND departure_date = %s AND departure_time = %s'

    # Check if it's a return flight - inbound selected
    if selected_inbound:
      # ... (add data to the tables, similar queries as presented above)
    ```
    *Explanation: Handling the purchase query is by far the most important interaction from the customer's side. First, insert a tuple into the `ticket` table. This is done so that the foreign key references are adhered to, with regards to the `purchase` and `ticket` table. Before continuing to enter information into the `purchase` table, check if the customer is booking a ticket for himself or someone else, and then add the data accordingly. Lastly, now that the ticket is generated and customer details are entered into the table, update the number of seats on the `flight` table to reflect a customer booking. Use the transaction methods learnt to rollback all the changes if any errors occur during this process.*

#### vii. Cancel Ticket
- **Description**: The customer will be able to cancel their ticket anytime before the flight as long as the scheduled departure is more than 24 hours away. Measures are taken both on the front-end and back-end to prevent rating flights before the arrival time.
- **SQL Queries**:
  - Query 1: Double-check if the ticket can be cancelled (adhere to the 24 hours policy).
    ```python
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
      # ... (will be discussed in Query 2)
    else:
      error = "Flight cannot be cancelled within 24 hours of departure."
      return render_template('customer-view-flights.html', error=error)
    ```
    *Explanation: Checks if the ticket can be cancelled by checking if the difference between the current time and the departure time is more than 24 hours. Else, an error will be thrown.*

  - Query 2: 
    ```python
    if can_cancel and (can_cancel['can_cancel'] == 1):
        # Delete the data from purchase and ticket table in the same order
        cursor.execute('DELETE FROM purchase WHERE ticketID = %s AND email_id = %s', (ticket_id_to_cancel, customer_email))
        cursor.execute('DELETE FROM ticket WHERE ticketID = %s', (ticket_id_to_cancel))
    ```
    *Explanation: Delete the data from the tables to cancel the ticket, and adhere to the foreign key constraints of the tables while following this process. Follow an efficient transaction method to prevent any unexpected errors in the database.*

  - Query 3: 
    ```python
    if can_cancel and (can_cancel['can_cancel'] == 1):
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
    ```
    *Explanation: Add an available seat to the flight since a customer has now cancelled the ticket. Follow an efficient transaction method to prevent any unexpected errors in the database.*

#### viii. Rate and Comment on Previous Flights
- **Description**: The customer will be able to rate and comment on the flights that he or the person he booked the flight for, had taken. Measures are taken both on the front-end and back-end to prevent rating flights before the arrival time.
- **SQL Queries**:
  - Query 1: Display all the previous flights that the customer has not rated yet.
    ```python
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
    ```
    *Explanation: Fetch the details of the previous flights of the customer and display for the customer to rate. They cannot technically rate until the flight has arrived at the destination airport (business logic). The query compares the system time against the arrival time and displays the data accordingly.*

  - Query 2: Add a customer review
    ```python
    # Insert the data from the form into the review table
    query = 'INSERT INTO review (ticketID, email_id, rate, comment) VALUES (%s, %s, %s, %s)'
    ```
    *Explanation: Once the checks are done above, the rating (a number between 1 to 5) and a comment will be passed to the database's `review` table.*

#### ix. Track my Spending
- **Description**: The customer will be able to track the overall spending in the past year, with an additional default view of monthly spending for the last 6 months. The view changes when the customer wishes to enter a date range and view the transactions within that range (total amount and monthly spending).
- **SQL Queries**:
  - Query 1: Fetch the total amount in the last 1 year.
    ```python
    # Query to get the total amount spent by the customer in the last 1 year
    total_spent_past_year_query = '''
        SELECT SUM(amount_paid) AS total_amount
        FROM `purchase`
        WHERE email_id = %s AND purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()
    '''
    ```
    *Explanation: Fetches the total amount spent in the past year by using the `CURDATE()` function to compare the system date and the purchase dates recorded in the database.*

  - Query 2: Fetch month-wise spending amounts for the past 6 months.
    ```python
    # Query to get the month-wise spending for the last six months
    monthly_spending_query = '''
        SELECT MONTHNAME(purchase_date) AS month, YEAR(purchase_date) AS year, 
            SUM(amount_paid) AS total_amount 
        FROM purchase 
        WHERE email_id = %s AND 
            purchase_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 MONTH) AND CURDATE() 
        GROUP BY month, year 
        ORDER BY year, month DESC;
    '''
    ```
    *Explanation: Fetches the total amounts grouped by the previous 6 months using similar logic as Query 1 to display the data.*

  - Query 3: Fetch the total amount and spending data within a given date range.
    ```python
     # If both start_date and end_date are provided, fetch the data within the range
    if start_date and end_date:
        # Total amount spent in the date range
        amount_in_date_range_query = '''
            SELECT SUM(amount_paid) AS total_amount
            FROM `purchase`
            WHERE email_id = %s AND purchase_date BETWEEN %s AND %s
        '''

    # Month wise spending in the date range
        date_range_monthly_spending_query = '''
        SELECT MONTHNAME(purchase_date) AS month, YEAR(purchase_date) AS year, 
            SUM(amount_paid) AS total_amount 
        FROM purchase 
        WHERE email_id = %s AND 
            purchase_date BETWEEN %s and %s 
        GROUP BY month, year 
        ORDER BY year, month DESC;
        '''
    ```
    *Explanation: Validate the date range given by the customer and show the total value of amount spent within the given range, and display a month-wise spending amounts table within the given range.*

#### x. View all Purchases
- **Description**: The customer will be able to view all the details associated with their purchases made with the account.
- **SQL Queries**:
  - Query 1: Fetch the ticket and purchase details to display all the purchases of the customer.
    ```python
     # Query to get the Purchase History and connected Ticket data
    spending_history_query = '''
            SELECT p.ticketID, p.amount_paid, p.purchase_date, p.purchase_time, 
            t.airline_name, t.flight_num ,t.departure_date, t.departure_time 
            FROM `purchase` as p ,`ticket` as t 
            WHERE t.ticketID = p.ticketID AND p.email_id = %s
            ORDER BY purchase_date DESC, purchase_time DESC;
            '''
    ```
    *Explanation: This query fetches all the relevant details needed by the customer while viewing all the transactions through the account before viewing the total amount.*
  - Query 2: Fetch the total amount spent by the customer since the creation of the account.
    ```python
    # Query to get the total amount spent by the customer in session
    total_spent_query = 'SELECT SUM(amount_paid) AS total_amount FROM `purchase` WHERE email_id = %s'
    ```
    *Explanation: Fetches the total amount spent by the customer without any filters, and displays all the transactions associated with the account (email_id).*


### 3. Airline Staff
The following are the use cases for when an airline staff member's login is authenticated.
#### i. registerStaff
- **Description**: This is used to register a new staff into the databse
- **SQL Queries**:
  - Query 1: this is used to make sure that this username does not already exist. Primary key check
    ```python
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    ```
  - Query 2: Is used to make sure that the airline exists in the database. Foreign key dependency check
    ```python
    airline_query = 'SELECT * FROM airline where airline_name = %s'
    ```

  - Query 3: This is the insert query to add staff into the database
    ```python
    insert_staff_query = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
    ```

  - Query 4: first query is used to insert phone number given by user into the database. The second query is used to make sure that phone number is not already in the database with that given user (ie a duplicate check)
    ```python
    insert_phone_query = 'INSERT INTO staff_phone VALUES(%s, %s)'
    phone_already_query = 'SELECT * from staff_phone where username = %s and phone_num = %s'
    ```

  - Query 5: first query is used to insert emails given by user into the database. The second query is used to make sure that email is not already in the database with that given user (ie a duplicate check)
    ```python
    insert_email_query = 'INSERT INTO staff_email VALUES(%s, %s)'
    email_already_query = 'SELECT * from staff_email where username = %s and email_id = %s'
    ```    


#### ii. loginStaff()
- **Description**: Need to make sure that the information given by the user matches a valid staff member in the DDB
- **SQL Queries**:
  - Query 1: Is a query to the DDB to check if the information given corresponds with a staff member in the DDB
    ``` python 
      query = 'SELECT * FROM airline_staff WHERE username = %s and pwd = %s'

    ```



#### iii. isNotValidStaff()
- **Description**: Is used to verify that a the person doing an action on the front end actually is a Staff member and therefore has the right to access certain information/links
- **SQL Queries**: 
  - Query 1: Need to make sure that the session user matches a valid staff member in the DDB
  ```python
    query = 'SELECT * FROM airline_staff WHERE username = %s and pwd = %s'

  ```
    



#### iv. view_flight()
- **Description**: needs to give all the flights by the airline in the enxt 30 days
- **SQL Queries**:
  - Query 1: selects from the flight table all flights that are between current date and 30 days out. 
    ```python
    thirty_day_query = 'SELECT * FROM flight WHERE airline_name = %s and CURRENT_DATE <= departure_date and departure_date <= DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY) ORDER BY departure_date DESC'
    ```



#### v. viewFlights()
- **Description**: needs to take in the information given by the user and create an SQL query that will return the list of flights based on the constraints given by the front end user.
- **SQL Queries**:
  - Query 1: Because the user can enter 0-5 attributes the sql query needs to be made by concatenating strings if information appears in the form.
    ```python
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

    ```


#### vi. change_status()
- **Description**: Staff member should be able to change the status of a given flight if they wish. This function obtains the flight that the user wants to change. this flight is sent to the changeStatus() function.
- **SQL Queries**:
  - Query 1: Selects the flight specified by the user in the front end
    ```python
    flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
    ```
    

#### vii. changeStatus()
- **Description**: changes the status of a given flight based on the information given by staff in the front end
- **SQL Queries**:
  - Query 1: first query updates the status of the flight specified by the user. The second query retrieves the flight from the data base with the updated flight status to show to the user 
    ```python
    flight_change_query = 'UPDATE flight set flight_status = %s where airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'

    flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'

    ```



#### viii. see_customers()
- **Description**: This function is used to see the customers that are on a given flight. Flight information is passed to the function using a form
- **SQL Queries**:
  - Query 1: This query is used to obtain the information of the flight in question.
    ```python
    flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
    ```
  - Query 2: This query is used to obtain the information for all the customers on that given flight
    ```python
    customer_query = 'SELECT * FROM purchase where ticketID in (SELECT ticketID from ticket where airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
    ```

#### ix. createNewFlight()
- **Description**: This function is used to create a new flight in the DDB. The problem is there are many foreign key dependencies that need to be checked before this can occur
- **SQL Queries**:
  - Query 1: This query is used to see if a flight like this already exists 
    ```python
      flight_exists_query = 'SELECT * FROM flight where airline_name = %s and flight_num = %s and departure_time = %s and departure_date = %s'

    ```
  - Query 2: query to see if the arrival airport exists in the DDB. Foreign Key dependency check
    ```python
    arrival_aiport_query = 'SELECT * FROM airport where code = %s'
    ```

    Query 3: query to see if the departure airport exists in DDB. Foreign Key dependency check
    ```python
    departure_aiport_query = 'SELECT * FROM airport where code = %s'
    ```

    Query 4: query to see if the airplane asked to be used is in the DDB system. Foreign Key dependency check
    ```python
  assigned_airplane_airline_query = 'SELECT * FROM airplane where airline_name = %s and airplaneID = %s'
    ```

    Query 5: query to get all the maintenances of a given airplane. This is then used to check if this flight can be created. If a maintenance is scheduled during proposed flight time then flight can not be created
    ```python
  maintenance_check_query = 'SELECT * FROM maintenance where airline_name = %s and airplaneID = %s'
    ```

    Query 6: Queries the airplane to see how many seats are availble on the aiplane. This becomes the number available on the flight
    ```python
    total_seats_query = 'SELECT num_of_seats from airplane where airline_name = %s and airplaneID = %s'
    ```

    Query 7: Inserts all the information into the flight table in the DDB
    ```python
    insert_flight_query = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    ```

     Query 8: queries the flight table for all flights that have departure dates in the next 30 days. They are returned in order by departure date
    ```python
    thirty_day_query = 'SELECT * FROM flight WHERE airline_name = %s and CURRENT_DATE <= departure_date and departure_date <= DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY) ORDER BY departure_date DESC'
    ```


#### x. createNewAirplane()
- **Description**: This function is used to create a new airplane in the DDB. There is a duplicate check that needs to occur
- **SQL Queries**:
  - Query 1: Queries the database for the airplane given the currect informaiton. If airplane already exists then can not create a duplicate
    ```python
      airplane_exists_query = 'SELECT * from airplane where airplaneID = %s and airline_name = %s'

    ```
 

#### xi. view_airplanes()
- **Description**: Is a function that is meant to get all the airplanes owned by the staff's airline.
- **SQL Queries**:
  - Query 1: gets all airplanes where airline_name is that of staff airline company
    ```python
      airplanes_query = 'SELECT * FROM airplane where airline_name = %s'

    ```


#### xii. createNewAirport()
- **Description**: Creates a new airport. But first must check if that airport already exists in the DDB
- **SQL Queries**:
  - Query 1: Query to see if an aiprot with the same code already exists
    ```python
  airport_exists_query = 'SELECT * FROM airport where code = %s'
    ```
  - Query 2: Inserts data given by staff member into the airport table in the DDB 
    ```python
    new_airport_insert = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s, %s)'
    ```


#### xiii. searchFlightRatings()
- **Description**: Used to see if a flight the staff member is searching for exists. If it does find that flight and send it to the printFlightRatings() functions
- **SQL Queries**:
  - Query 1: queries the database for a certain flight based on the information given by staff.
    ```python
  flight_exists_query = 'SELECT * FROM flight where airline_name = %s and flight_num = %s and departure_time = %s and departure_date = %s'
    ```


#### xiv. printFlightRatings(flight)
- **Description**: This takes in a flight as a parameter and then queries the review table to retrieve all the reviews with that flight
- **SQL Queries**: 
  - Query 1: Subquery gets all the ticketID in the ticket table that correspond to the flight. Then in the review tables all ticketID that are in the subquery are selected.
    ```python
  reviews_query = 'SELECT * FROM review where ticketID in (SELECT ticketID FROM ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
    ```
  - Query 2: basically the same as the query above in terms of subquery but instead of getting all the reviews just gets a single value for the average of the ratings for all the reviews
    ```python
  review_avg_query = 'SELECT avg(rate) as avgRate FROM review where ticketID in (SELECT ticketID FROM ticket WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s)'
    ```


#### xv. view_reviews()
- **Description**: This function is called when a staff member clicks on the reviews link of a flight (in the search function). The parameters are passed through the URL and the flight is found and then passed to the printFlightRatings
- **SQL Queries**:
  - Query 1: Queries to find the flight so it can be passed to the printFlight Ratings
    ```python
  flight_query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s and departure_date = %s and departure_time = %s'
    ```


#### xvi. scheduleMaintenance()
- **Description**: Is used to schedule a maintenance for a flight. Need to check if airplane exists and whether the airplane is already scheduled for flight during the proposed maintenance time
- **SQL Queries**:
  - Query 1: quries DDB to retrieve airplane which the staff is trying to schedule maintenace
    ```python
      airplane_query = 'SELECT * FROM airplane WHERE airline_name = %s and airplaneID = %s'

    ```
  - Query 2: queries DDB to find all the flights using the given airplane
    ```python
  flight_check_query = 'SELECT * from flight where assigned_airplaneID = %s and assigned_airplane_airline = %s'
    ```
  - Query 3: Inserts all the information for a maintenance if one is allowed
    ```python
    maintenance_insert_query = 'INSERT INTO maintenance VALUES (%s, %s, %s, %s, %s, %s)'
    ```


#### xvii. view_frequent_customers()
- **Description**: function is called to view the customers who most frequently use the airline (most flights taken/booked)
- **SQL Queries**: 
  - Query 1: Gets all the information of the customers on the staff airline and retrieves the number of tickets they have bought 
    ```python
  most_frequent_query = 'SELECT email_id, first_name, last_name, date_of_birth, count(*) as frequency from purchase natural join customer natural join ticket where airline_name = %s group by email_id order by frequency desc'
    ```



#### xviii. view_customer_flights()
- **Description**: This function is called when the staff clicks on a customer in the view_frequent_customers() page. It allows them to see all of the flight they have taken and have booked
- **SQL Queries**:
  - Query 1: This query is used to retrieve the customer in question. Needed as the information is passed through URL
    ```python
    customer_query = 'SELECT * from customer where email_id = %s'
    ```
  - Query 2: This gets all the information about the flights the customer in question has taken on staff airline. Because of the joining of three tables * could not be used and thus all attributes wanted needed to be listed out
    ```python
  flights_query = 'SELECT airline_name, departure_airport, arrival_airport, assigned_airplane_airline, assigned_airplaneID, flight_num, departure_date, departure_time, arrival_date, arrival_time, base_price_ticket, flight_status, total_seats, available_seats from (customer, purchase) natural join ticket natural join flight where customer.email_id = purchase.email_id and customer.email_id = %s and airline_name = %s'
    ```


#### xix. view_earned_revenue()
- **Description**: Function is used to get all the revenue of the airline in the past month and the past year
- **SQL Queries**: 
  - Query 1: Gets the sum of all the amount_paid by customers from the purchase table. This is designed to show all the money in the past month based on the purchase date not the flight time
    ```python
  monthly_query = 'SELECT sum(amount_paid) as month_amt from purchase natural join ticket where airline_name = %s and purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)'
    ```
  - Query 2: Gets the sum of all the amount_paid by customers in form the purchase table over the last year. Purchase date is in quesiton not the departure time of flights
    ```python
  yearly_query = 'SELECT sum(amount_paid) as year_amt from purchase natural join ticket where airline_name = %s and purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)'
    ```






## License

This project is developed as a part of *CS-UY 3083: Introduction to Databases* at NYU Tandon School of Engineering and is intended for educational purposes only. While this project is not covered under any formal open-source license, any use, modification, or distribution of the project's code or documentation must be consulted with and approved by the contributors of the project. 

Please contact [Pranav](mailto:sri.pranav@nyu.edu) or [Theo](mailto:tlw9927@nyu.edu) for any inquiries regarding the use or modification of this project.

## Contact Information
 - [Sri Pranav Srivatsavai](mailto:sri.pranav@nyu.edu)
 - [Theo Welckle](mailto:tlw9927@nyu.edu)

## References and Acknowledgements

This project benefited from a range of supportive resources, ensuring a thorough understanding and effective problem-solving:

- **AI Tools**: We occasionally used AI tools for debugging and to gain insights into how similar features are implemented in industry applications. These tools were not used to complete the primary educational objectives of this project but rather to assist in specific syntax challenges (mainly Flask and Jinja2) we faced during the course of our project.

- **Online Communities**: Platforms like Stack Overflow were helpful for solving specific coding challenges.

The core development and problem-solving were carried out independently by us. We believe in the ethical and responsible use of such resources, ensuring they complement our learning without overshadowing the primary educational objectives of this project.

