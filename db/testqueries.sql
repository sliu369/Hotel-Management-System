my_test_query = '''
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema');
    '''

hotel_chain_details = '''
    SELECT 
    hc.chain_ID, 
    hc.name, 
    hc.office_address,
    string_agg(DISTINCT hce.hotel_chain_email, ', ') AS emails,
    string_agg(DISTINCT hcp.chain_phone_num, ', ') AS phone_numbers
    FROM Hotel_Chain hc
    LEFT JOIN Hotel_Chain_Email hce ON hc.chain_ID = hce.chain_ID
    LEFT JOIN Hotel_Chain_Phone hcp ON hc.chain_ID = hcp.chain_ID
    GROUP BY hc.chain_ID, hc.name, hc.office_address;
    '''

list_hotels_in_chain = "SELECT hotel_ID, hotel_email, addresss, category FROM Hotel WHERE chain_ID = " + chain_ID + ";"

search_room_by_date = '''
SELECT r.room_ID, r.room_number, r.price, r.capacity, r.view_type, r.is_extendable
FROM Room r WHERE r.room_ID NOT IN (
    SELECT b.room_ID
    FROM Booking b
    WHERE (b.in_date, b.out_date) OVERLAPS ('
    ''' + in_date + "'::date, '" + out_date + "'::date));"

insert_booking = '''
INSERT INTO Booking (booking_ID, room_ID, customer_ID, in_date, out_date, employee_ID)
VALUES (''' + booking_ID + ", " + room_id + ", " + customer_ID + ", '" + in_date + "', '" + out_date + "', " + employee_ID + ");"

#Insert, update, delete for customer
insert_customer = '''
INSERT INTO Customer (customer_ID, first_name, last_name, address, registration_date, type_of_ID)
VALUES (''' + customer_ID + ", '" + first_name + "', '" + last_name + "', '" + address + "', '" + registration_date + "', '" + type_of_ID + "');"

update_customer = '''
UPDATE Customer
SET first_name = '{first_name}',
    last_name = '{ast_name}',
    address = '{address}',
    type_of_ID = '{type_of_ID}'
WHERE customer_ID = {customer_ID};'''

delete_customer = '''DELETE FROM Customer WHERE customer_ID = {customer_ID};'''

#Insert, update, delete for Employees
insert_employee = '''
INSERT INTO Employee (employee_ID, hotel_ID, sin_number, first_name, last_name)
VALUES ({employee_ID}, {hotel_ID}, '{sin_number}', '{first_name}', '{last_name}');'''

update_employee = '''
UPDATE Employee
SET hotel_ID = '{hotel_ID}' WHERE employee_ID = {employee_ID};''' 
#only allowed to change the hotel they work in

delete_employee = '''
DELETE FROM Employee WHERE employee_ID = {employee_ID};'''

#Insert, update, delete for Hotel
insert_hotel = '''
INSERT INTO Hotel (hotel_ID, chain_ID, hotel_email, address, category)
VALUES ({hotel_ID}, {chain_ID}, '{hotel_email}', '{address}', '{category}');'''

update_hotel = '''
UPDATE Hotel
SET hotel_email = '{hotel_email}',
    address = '{address}',
    category = '{category}'
WHERE hotel_ID = {hotel_ID};'''

delete_hotel = '''
DELETE FROM Hotel WHERE hotel_ID = {hotel_ID};'''

#Insert, update, delete for Room
insert_room = '''
INSERT INTO Room (room_ID, hotel_ID, room_number, price, capacity, view_type, is_extendable)
VALUES ({room_ID}, {hotel_ID}, '{room_number}', {price}, {capacity}, '{view_type}', {is_extendable});'''

update_room = '''
UPDATE Room
SET price = {price},
    capacity = {capacity},
    view_type = '{city_view}',
    is_extendable = {is_extendable}
WHERE room_ID = {room_ID};'''

delete_room = '''DELETE FROM Room WHERE room_ID = {room_ID};'''

#Create a rental or turn a booking into rental
insert_rental = '''
INSERT INTO Rental (renting_id, room_ID, customer_ID, in_date, out_date, employee_ID, booking_ID, hotel_ID, rental_price)
VALUES ({rentingidD}, {room_I}, {customer_ID}, '{in_date}', '{out_date}', {employee_ID}, {booking_ID}, {hotel_ID}, {rental_price});'''

booking_to_rental = '''
INSERT INTO Rental (renting_id, room_ID, customer_ID, in_date, out_date, employee_ID, booking_ID, hotel_ID, rental_price)
SELECT {renting_id}, b.room_ID, b.customer_ID, b.in_date, b.out_date, b.employee_ID, b.booking_ID, b.hotel_ID, r.price
FROM Booking b
JOIN Room r ON b.room_ID = r.room_ID
WHERE b.booking_ID = {booking_ID};'''



