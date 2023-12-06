# Airline Ticket Reservation System
CS-UY 3083 Introduction to Databases <br/>
NYU Tandon School of Enginnering <br/>
Professor Ratan Dey <br/>
Fall 2023 <br/>

## Introduction
Briefly describe your application, its purpose, and its main functionalities.

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

### Public (No Users Logged In)
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

### Customer (Login Authenticated)
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

### Airline Staff (Login Authenticated)
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


## Additional Features
If your application has any additional features, mention them here.

## License

This project is developed as a part of *CS-UY 3083: Introduction to Databases* at NYU Tandon School of Engineering and is intended for educational purposes only. While this project is not covered under any formal open-source license, any use, modification, or distribution of the project's code or documentation must be consulted with and approved by the contributors of the project. 

Please contact [Pranav](mailto:sri.pranav@nyu.edu) or [Theo](mailto:tlw9927@nyu.edu) for any inquiries regarding the use or modification of this project.

## Contact Information
 - [Sri Pranav Srivatsavai](mailto:sri.pranav@nyu.edu)
 - [Theo Welckle](mailto:tlw9927@nyu.edu)


