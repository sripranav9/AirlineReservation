#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
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
        return render_template('search.html', outbound_flights=outbound_flights, inbound_flights=inbound_flights, trip_type=trip_type)
    
    # If method is GET, just render the search form
    return render_template('index.html')

		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
