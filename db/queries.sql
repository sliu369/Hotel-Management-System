-- query 1 aggregated query - ROUTES.PY LINE 231
SELECT MAX(renting_id) FROM rental

-- query 2 - queries.py line 533
SELECT h.hotel_id, hc.name AS chain_name, h.area, h.address
    FROM hotel h JOIN hotel_chain hc ON h.chain_id = hc.chain_id
    ORDER BY hc.name, h.area, h.address

--query 3 - routes.py line 616
SELECT r.*, hc.name AS chain_name, h.area, h.address
    FROM room r
    JOIN hotel h ON r.hotel_id = h.hotel_id
    JOIN hotel_chain hc ON h.chain_id = hc.chain_id

--query 4 nested query - routes.py line 55
SELECT r.*, h.area, h.address AS hotel_address
    FROM room r
    JOIN hotel h ON r.hotel_id = h.hotel_id
    WHERE r.hotel_id = :hid AND r.capacity >= :cap
    AND NOT EXISTS (
        SELECT 1 FROM booking b
        WHERE b.room_id = r.room_id
            AND b.in_date < :checkout AND b.out_date > :checkin
    )
    AND NOT EXISTS (
        SELECT 1 FROM rental rt
        WHERE rt.room_id = r.room_id
            AND rt.in_date < :checkout AND rt.out_date > :checkin
    )

-- parameters that makes this work:
params = {
    "hid": hotel_id,
    "cap": capacity,
    "checkin": checkin,
    "checkout": checkout
            }