-- Function to archive booking
CREATE OR REPLACE FUNCTION archive_booking_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO booking_archive (
        original_booking_ID, room_ID, customer_ID, 
        in_date, out_date, hotel_ID
    )
    VALUES (
        NEW.booking_ID, NEW.room_ID, NEW.customer_ID,
        NEW.in_date, NEW.out_date, NEW.hotel_ID
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to archive a booking
CREATE TRIGGER trigger_archive_booking
AFTER INSERT ON Booking
FOR EACH ROW
EXECUTE FUNCTION archive_booking_on_insert(); 

-- Function to archive rental
CREATE OR REPLACE FUNCTION archive_rental_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO rental_archive (
        original_rental_ID, room_ID, customer_ID, 
        in_date, out_date, employee_ID, original_booking_ID, 
        rental_price, hotel_ID
    )
    VALUES (
        NEW.renting_id, NEW.room_ID, NEW.customer_ID,
        NEW.in_date, NEW.out_date, NEW.employee_ID, NEW.booking_ID,
        NEW.rental_price, NEW.hotel_ID
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to archive rental
CREATE TRIGGER trigger_archive_rental
AFTER INSERT ON Rental
FOR EACH ROW
EXECUTE FUNCTION archive_rental_on_insert();