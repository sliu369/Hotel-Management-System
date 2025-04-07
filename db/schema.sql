-- 1. Hotel_Chain
CREATE TABLE Hotel_Chain (
    chain_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    office_address VARCHAR(255) NOT NULL
);

-- 2. Hotel_Chain_Email
CREATE TABLE hotel_chain_email (
    chain_id INT NOT NULL,
    hotel_chain_email VARCHAR(255) NOT NULL,
    CHECK (position('@' in hotel_chain_email) > 1),
    PRIMARY KEY (chain_id, hotel_chain_email),
    FOREIGN KEY (chain_id)
        REFERENCES hotel_chain(chain_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 3. Hotel_Chain_Phone
CREATE TABLE Hotel_Chain_Phone (
    chain_id INT NOT NULL,
    chain_phone_num BIGINT NOT NULL,
    PRIMARY KEY (chain_id, chain_phone_num),
    FOREIGN KEY (chain_id)
        REFERENCES Hotel_Chain(chain_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 4. Hotel
CREATE TABLE hotel (
    hotel_id INT PRIMARY KEY,
    chain_id INT NOT NULL,
    hotel_email VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    area VARCHAR(255) NOT NULL,
    category INTEGER NOT NULL,
    CHECK (position('@' in hotel_email) > 1),
    CHECK (category BETWEEN 1 AND 5),
    FOREIGN KEY (chain_id)
        REFERENCES hotel_chain(chain_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 5. Hotel_Phone
CREATE TABLE Hotel_Phone (
    hotel_id INT NOT NULL,
    hotel_phone_num BIGINT NOT NULL,
    PRIMARY KEY (hotel_id, hotel_phone_num),
    FOREIGN KEY (hotel_id)
        REFERENCES Hotel(hotel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 6. Room
CREATE TABLE Room (
    room_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    capacity INT NOT NULL,
    view_type VARCHAR(50),
    is_extendable BOOLEAN NOT NULL,
    CHECK (view_type IN ('sea view', 'mountain view')),
    FOREIGN KEY (hotel_id)
        REFERENCES Hotel(hotel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    UNIQUE (hotel_id, room_number)
);

-- 7. Room_Amenities
CREATE TABLE Room_Amenities (
    room_id INT NOT NULL,
    amenity VARCHAR(100) NOT NULL,
    PRIMARY KEY (room_id, amenity),
    FOREIGN KEY (room_id)
        REFERENCES Room(room_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 8. Room_Problems
CREATE TABLE Room_Problems (
    room_id INT NOT NULL,
    problem_description VARCHAR(255) NOT NULL,
    PRIMARY KEY (room_id, problem_description),
    FOREIGN KEY (room_id)
        REFERENCES Room(room_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 9. Customer
CREATE TABLE Customer (
    customer_ID INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    registration_date DATE NOT NULL,
    type_of_ID VARCHAR(50)
);

-- 10. Employee
CREATE TABLE Employee (
    employee_ID INT PRIMARY KEY,
    hotel_ID INT NOT NULL,
    sin_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel(hotel_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 11. Employee_Role
CREATE TABLE Employee_Role (
    employee_ID INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (employee_ID, role),
    FOREIGN KEY (employee_ID)
        REFERENCES Employee(employee_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 12. Booking
CREATE TABLE Booking (
    booking_ID INT PRIMARY KEY,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    employee_ID INT NOT NULL,
    hotel_ID INT NOT NULL,
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel_Chain(chain_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (customer_ID)
        REFERENCES Customer(customer_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (employee_ID)
        REFERENCES Employee(employee_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 13. Rental
CREATE TABLE Rental (
    renting_id INT PRIMARY KEY,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    employee_ID INT NOT NULL,
    booking_ID INT,
    rental_price DECIMAL(10, 2) NOT NULL,
    hotel_ID INT NOT NULL,
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel_Chain(chain_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (customer_ID)
        REFERENCES Customer(customer_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (employee_ID)
        REFERENCES Employee(employee_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (booking_ID)
        REFERENCES Booking(booking_ID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);




--------


-- 1. Hotel_Chain
CREATE TABLE Hotel_Chain (
    chain_ID INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    office_address VARCHAR(255) NOT NULL
);

-- 2. Hotel_Chain_Email
CREATE TABLE Hotel_Chain_Email (
    chain_ID INT NOT NULL,
    hotel_chain_email VARCHAR(255) NOT NULL,
    CHECK (position('@' in hotel_chain_email) > 1),
    PRIMARY KEY (chain_ID, hotel_chain_email),
    FOREIGN KEY (chain_ID)
        REFERENCES Hotel_Chain(chain_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 3. Hotel_Chain_Phone
CREATE TABLE Hotel_Chain_Phone (
    chain_id INT NOT NULL,
    chain_phone_num BIGINT NOT NULL,
    PRIMARY KEY (chain_id, chain_phone_num),
    FOREIGN KEY (chain_id)
        REFERENCES Hotel_Chain(chain_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 4. Hotel
CREATE TABLE Hotel (
    hotel_ID INT PRIMARY KEY,
    chain_ID INT NOT NULL,
    hotel_email VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    area VARCHAR(255) NOT NULL,
    category INTEGER NOT NULL,
    CHECK (position('@' in hotel_email) > 1),
    CHECK (category BETWEEN 1 AND 5),
    FOREIGN KEY (chain_ID)
        REFERENCES Hotel_Chain(chain_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

- 5. Hotel_Phone
CREATE TABLE Hotel_Phone (
    hotel_id INT NOT NULL,
    hotel_phone_num BIGINT NOT NULL,
    PRIMARY KEY (hotel_id, hotel_phone_num),
    FOREIGN KEY (hotel_id)
        REFERENCES Hotel(hotel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 6. Room
CREATE TABLE Room (
    room_ID INT PRIMARY KEY,
    hotel_ID INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    capacity INT NOT NULL,
    view_type VARCHAR(50),
    is_extendable BOOLEAN NOT NULL,
    CHECK (view_type IN ('sea view', 'mountain view')),
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel(hotel_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 7. Room_Amenities
CREATE TABLE Room_Amenities (
    room_ID INT NOT NULL,
    amenity VARCHAR(100) NOT NULL,
    PRIMARY KEY (room_ID, amenity),
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 8. Room_Problems
CREATE TABLE Room_Problems (
    room_ID INT NOT NULL,
    problem_description VARCHAR(255) NOT NULL,
    PRIMARY KEY (room_ID, problem_description),
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 9. Customer
CREATE TABLE Customer (
    customer_ID INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    registration_date DATE NOT NULL,
    type_of_ID VARCHAR(50) NOT NULL
);

-- 10. Employee
CREATE TABLE Employee (
    employee_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    sin_number CHAR(9) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (hotel_id)
        REFERENCES hotel(hotel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 11. Employee_Role
CREATE TABLE Employee_Role (
    employee_ID INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (employee_ID, role),
    FOREIGN KEY (employee_ID)
        REFERENCES Employee(employee_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 12. Booking
CREATE TABLE Booking (
    booking_ID INT PRIMARY KEY,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    hotel_ID INT NOT NULL,
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel(hotel_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (customer_ID)
        REFERENCES Customer(customer_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
);

-- 13. Rental
CREATE TABLE Rental (
    renting_id INT PRIMARY KEY,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    employee_ID INT NOT NULL,
    booking_ID INT,
    rental_price DECIMAL(10, 2) NOT NULL,
    hotel_ID INT NOT NULL,
    FOREIGN KEY (hotel_ID)
        REFERENCES Hotel(hotel_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (room_ID)
        REFERENCES Room(room_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (customer_ID)
        REFERENCES Customer(customer_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (employee_ID)
        REFERENCES Employee(employee_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (booking_ID)
        REFERENCES Booking(booking_ID)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);
 
-- 14. Booking_Archive
CREATE TABLE Booking_Archive (
    booking_archive_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    original_booking_ID INT NOT NULL,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    hotel_ID INT NOT NULL
);

--15. Rental_Archive
CREATE TABLE Rental_Archive (
    rental_archive_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    original_rental_ID INT NOT NULL,
    room_ID INT NOT NULL,
    customer_ID INT NOT NULL,
    in_date DATE NOT NULL,
    out_date DATE NOT NULL,
    employee_ID INT NOT NULL,
    original_booking_ID INT,
    rental_price DECIMAL(10, 2) NOT NULL,
    hotel_ID INT NOT NULL
);