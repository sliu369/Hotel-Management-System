-- Create index on booking, with room_id and in/out date
CREATE INDEX idx_booked_room_dates 
ON booking (in_date, out_date);
/*
- This index accelerates the 'search_rooms_by_date' query that searches for available rooms within given dates.
- Slows the down insert/update/delete operations for booking but increase the read time.
- Index is needed because searching for available rooms by date range is a very frequent function.
*/

-- 2. Create index on room, with price
CREATE INDEX idx_room_price
ON room(price);
/*
- Accelerates for queries that filters room, sorts room, and aggregates base on price.
- Uses a B-tree index for efficient date range scans (BETWEEN, >, <).
- Insert/update/delete will be slower because the index needs to be updated, however,
    the tradeoff is worth it because filter/sort by room price is a very essential function
    for a hotel app.
*/

-- 3. Index for customer-centric rental history lookups
CREATE INDEX idx_archived_rental_customer
ON rental_archive (customer_id);
/*
- Allows the database to quickly locate all archived rentals associated with a specific 
    customer_id without scanning the entire rental_archive table.
- Archived data is rarely modified after insertion, thus the write penalty is minimal 
    compared to read performance gains.
- Very helpful in the case of customer support, where looking up a customer's rental history
    is required.
*/