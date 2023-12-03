-- All future flights in the system
SELECT * FROM flight WHERE departure_date > CURRENT_DATE OR (departure_date = CURRENT_DATE AND departure_time > CURRENT_TIME);

-- Show all the delayed flights in the system
SELECT * FROM flight WHERE flight_status = "delayed";

-- Customer names who bought the tickets 
-- (customer names ON the ticket)
SELECT first_name, last_name FROM purchase;
-- OR
-- (customer names who purchased the ticket)
SELECT c.first_name, c.last_name
FROM purchase p, customer c
WHERE p.email_id = c.email_id;

-- Airplanes owned by Jet Blue
SELECT airplaneID FROM airplane WHERE airline_name = "Jet Blue";