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

Key features include:
- Functional interfaces for flight searches, ticket bookings, and user management.
- Dedicated login and registration modules for enhanced security.
- Comprehensive access to flight information for customers, including past, current, and future flights.
- Extensive flight management options for airline staff, encompassing flight creation, status updates, and customer service.

## Features
[List the key features of your application.]

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
#### View Public Information
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
    *Explanation: The query fetches all the required details from the `flight` table by checking for flights that are not cancelled and have atleast 1 available seat. The dynamic pricing follows the strategy where the ticket will cost 25% more than the base price if the flight capacity is above 80%.*
  - Query 2: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*

#### [Use Case Heading]
- **Description**: [Briefly describe what this use case does.]
- **SQL Queries**:
  - Query 1: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*

### 2. Customer
The following are the use cases for when a customer's login is authenticated.
#### [Use Case Heading]
- **Description**: [Briefly describe what this use case does.]
- **SQL Queries**:
  - Query 1: `SELECT ... FROM ... WHERE ...`
    - *Explanation*: [Explain what this query does and why it's used in this context.]
  - Query 2: `INSERT INTO ... VALUES (...)`
    - *Explanation*: [Explanation of the second query.]

#### [Use Case Heading]
- **Description**: [Briefly describe what this use case does.]
- **SQL Queries**:
  - Query 1: `SELECT ... FROM ... WHERE ...`
    - *Explanation*: [Explain what this query does and why it's used in this context.]
  - Query 2: `INSERT INTO ... VALUES (...)`
    - *Explanation*: [Explanation of the second query.]

### 3. Airline Staff
The following are the use cases for when an airline staff member's login is authenticated.
#### [Use Case Heading]
- **Description**: [Briefly describe what this use case does.]
- **SQL Queries**:
  - Query 1: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*
  - Query 2: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*

#### [Use Case Heading]
- **Description**: [Briefly describe what this use case does.]
- **SQL Queries**:
  - Query 2: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*
  - Query 2: [Short Description]
    ```python
    #paste the sql query from the flask app here
    ```
    *Explanation: [Explanation of the query.]*


## Additional Features
If your application has any additional features, mention them here.

## License

This project is developed as a part of *CS-UY 3083: Introduction to Databases* at NYU Tandon School of Engineering and is intended for educational purposes only. While this project is not covered under any formal open-source license, any use, modification, or distribution of the project's code or documentation must be consulted with and approved by the contributors of the project. 

Please contact [Pranav](mailto:sri.pranav@nyu.edu) or [Theo](mailto:tlw9927@nyu.edu) for any inquiries regarding the use or modification of this project.

## Contact Information
 - [Sri Pranav Srivatsavai](mailto:sri.pranav@nyu.edu)
 - [Theo Welckle](mailto:tlw9927@nyu.edu)


