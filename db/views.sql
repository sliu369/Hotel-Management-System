-- View 1
CREATE VIEW view_one AS
SELECT h.area, COUNT(*) AS available_rooms
FROM room r
JOIN hotel h ON r.hotel_id = h.hotel_id
WHERE NOT EXISTS (
    SELECT 1 FROM booking b
    WHERE b.room_id = r.room_id
      AND b.in_date <= CURRENT_DATE
      AND b.out_date > CURRENT_DATE
)
AND NOT EXISTS (
    SELECT 1 FROM rental rt
    WHERE rt.room_id = r.room_id
      AND rt.in_date <= CURRENT_DATE
      AND rt.out_date > CURRENT_DATE
)
GROUP BY h.area;


-- Query View 1
SELECT * FROM AvailableRoomsPerArea;


-- View 2
CREATE VIEW Hotel_Aggregated_Capacity AS
SELECT 
    h.hotel_ID,
    SUM(r.capacity) AS total_room_capacity
FROM Hotel h
LEFT JOIN Room r ON h.hotel_ID = r.hotel_ID
GROUP BY h.hotel_ID;

Example Query:
SELECT * FROM Hotel_Aggregated_Capacity WHERE hotel_ID = {hotel_ID};