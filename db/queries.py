def get_total_room (hotel_id: int) -> str:

   return  f'''
    SELECT COUNT(*) AS number_of_rooms
    FROM Room
    WHERE hotel_id = {hotel_id};
    '''

def hotel_chain_details () -> str:
    return '''
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

def list_hotels_in_chain (chain_id: int):
    return f"SELECT hotel_ID, hotel_email, addresss, category FROM Hotel WHERE chain_ID = {chain_id};"


def search_rooms_by_date(in_date: str, out_date: str) -> str:
    return f"""
        SELECT r.room_id, r.room_number, r.price, r.capacity, r.view_type, r.is_extendable
        FROM room r
        WHERE r.room_id NOT IN (
            SELECT b.room_id
            FROM booking b
            WHERE (b.in_date, b.out_date) OVERLAPS ('{in_date}'::date, '{out_date}'::date)
        );
    """ 

# =====================================================================
# Booking operations
# =====================================================================
def insert_booking(booking_id: int, room_id: int, customer_id: int, in_date: str, 
                   out_date: str, employee_id: int, hotel_id: int) -> str:
    return f"""
        INSERT INTO booking (
            booking_id, room_id, customer_id, 
            in_date, out_date, employee_id, hotel_id
        )
        VALUES (
            {booking_id}, {room_id}, {customer_id}, 
            '{in_date}', '{out_date}', {employee_id}, {hotel_id}
        );
    """

def delete_booking(booking_id: int) -> str:
    return f"DELETE FROM booking WHERE booking_id = {booking_id};"

# =====================================================================
# Rental operations
# =====================================================================
def insert_rental(renting_id: int, room_id: int, customer_id: int, in_date: str, out_date: str, 
    employee_id: int,  booking_id: int | None, hotel_id: int, rental_price: float) -> str:
    if booking_id == None:
        booking_id_value = "NULL"
    else:
        booking_id_value = booking_id

    return f"""
        INSERT INTO rental (
            renting_id, room_id, customer_id, in_date, 
            out_date, employee_id, booking_id, hotel_id, rental_price
        )
        VALUES (
            {renting_id}, {room_id}, {customer_id}, '{in_date}', '{out_date}', {employee_id}, 
            {booking_id_value}, {hotel_id}, {rental_price}
        );
    """

def delete_rental(renting_id: int) -> str:
    return f"DELETE FROM rental WHERE renting_id = {renting_id};"

# =====================================================================
# Customer operations
# =====================================================================
def insert_customer(customer_id: int, first_name: str, last_name: str, address: str, registration_date: str, type_of_id: str) -> str:
    return f"""
        INSERT INTO customer (customer_id, first_name, last_name, address, registration_date, type_of_id)
        VALUES ({customer_id}, '{first_name}', '{last_name}', '{address}', '{registration_date}', '{type_of_id}');
    """

def update_customer(customer_id: int, first_name: str, last_name: str, address: str, type_of_id: str) -> str:
    return f"""
        UPDATE customer
        SET first_name = '{first_name}',
            last_name = '{last_name}',
            address = '{address}',
            type_of_id = '{type_of_id}'
        WHERE customer_id = {customer_id};
    """

def delete_customer(customer_id: int) -> str:
    return f"DELETE FROM customer WHERE customer_id = {customer_id};"

# =====================================================================
# Employee operations
# =====================================================================
def insert_employee(employee_id: int, hotel_id: int, sin_number: str, first_name: str, last_name: str) -> str:
    return f"""
        INSERT INTO employee (employee_id, hotel_id, sin_number, first_name, last_name)
        VALUES ({employee_id}, {hotel_id}, '{sin_number}', '{first_name}', '{last_name}');
    """

def update_employee_hotel(employee_id: int, hotel_id: int) -> str:
    return f"UPDATE employee SET hotel_id = {hotel_id} WHERE employee_id = {employee_id};"

def delete_employee(employee_id: int) -> str:
    return f"DELETE FROM employee WHERE employee_id = {employee_id};"

# =====================================================================
# Hotel operations
# =====================================================================
def insert_hotel(hotel_id: int, chain_id: int, hotel_email: str, address: str, area: str, category: int) -> str:
    return f"""
        INSERT INTO hotel (hotel_id, chain_id, hotel_email, address, area, category)
        VALUES ({hotel_id}, {chain_id}, '{hotel_email}', '{address}', '{area}', {category});
    """

def update_hotel(hotel_id: int, hotel_email: str, address: str, area: str, category: int) -> str:
    return f"""
        UPDATE hotel
        SET hotel_email = '{hotel_email}',
            address = '{address}',
            area = '{area}',
            category = {category}
        WHERE hotel_id = {hotel_id};
    """

def delete_hotel(hotel_id: int) -> str:
    return f"DELETE FROM hotel WHERE hotel_id = {hotel_id};"

# =====================================================================
# Room operations
# =====================================================================
def insert_room(room_id: int, hotel_id: int, room_number: str, price: float, capacity: int, view_type: str, is_extendable: str) -> str:
    return f"""
        INSERT INTO room (room_id, hotel_id, room_number, price, capacity, view_type, is_extendable)
        VALUES ({room_id}, {hotel_id}, '{room_number}', {price}, {capacity}, '{view_type}', {is_extendable});
    """

def update_room(room_id: int, price: float, capacity: int, view_type: str, is_extendable: bool) -> str:
    return f"""
        UPDATE room
        SET price = {price},
            capacity = {capacity},
            view_type = '{view_type}',
            is_extendable = {str(is_extendable).lower()}
        WHERE room_id = {room_id};
    """

# =====================================================================
# Hotel_Chain_Email operations
# =====================================================================
def insert_hotel_chain_email(chain_id: int, email: str) -> str:
    return f"""
        INSERT INTO hotel_chain_email (chain_id, hotel_chain_email)
        VALUES ({chain_id}, '{email}');
    """

def delete_hotel_chain_email(chain_id: int, email: str) -> str:
    return f"""
        DELETE FROM hotel_chain_email
        WHERE chain_id = {chain_id} AND hotel_chain_email = '{email}';
    """

# =====================================================================
# Hotel_Chain_Phone operations
# =====================================================================
def insert_hotel_chain_phone(chain_id: int, phone_num: int) -> str:
    return f"""
        INSERT INTO hotel_chain_phone (chain_id, chain_phone_num)
        VALUES ({chain_id}, {phone_num});
    """

def delete_hotel_chain_phone(chain_id: int, phone_num: int) -> str:
    return f"""
        DELETE FROM hotel_chain_phone
        WHERE chain_id = {chain_id} AND chain_phone_num = {phone_num};
    """

# =====================================================================
# Hotel_Phone operations
# =====================================================================
def insert_hotel_phone(hotel_id: int, phone_num: int) -> str:
    return f"""
        INSERT INTO hotel_phone (hotel_id, hotel_phone_num)
        VALUES ({hotel_id}, {phone_num});
    """

def delete_hotel_phone(hotel_id: int, phone_num: int) -> str:
    return f"""
        DELETE FROM hotel_phone
        WHERE hotel_id = {hotel_id} AND hotel_phone_num = {phone_num};
    """

def search_room(in_date: str, out_date: str, capacity: int|None, hotel_chain: str|None, 
                category: int|None, min_rooms: str|None, max_rooms: str|None, 
                min_price: str|None, max_price: str|None) -> str:
    
    conditions = []
    
    # Capacity filter
    if capacity is not None:
        conditions.append(f"r.capacity = {capacity}")
    
    # Hotel chain filter
    if hotel_chain is not None:
        conditions.append(f"hc.name = {hotel_chain})")
    
    # Category filter
    if category is not None:
        conditions.append(f"h.category = {category}")
    
    # Price range filter
    if min_price is not None:
        conditions.append(f"r.price >= {min_price}")
    if max_price is not None:
        conditions.append(f"r.price <= {max_price}")
    
    # Room count filter
    room_count_conds = []
    if min_rooms is not None:
        room_count_conds.append(f"room_count >= {min_rooms}")
    if max_rooms is not None:
        room_count_conds.append(f"room_count <= {max_rooms}")
    if room_count_conds:
        conditions.append(" AND ".join(room_count_conds))
    
    # Build WHERE clause
    where_clause = ""
    if conditions:
        where_clause = " AND " + " AND ".join(conditions)
    
    return f"""
        WITH hotel_room_counts AS (
            SELECT 
                h.hotel_id,
                COUNT(r_inner.room_id) AS room_count
            FROM hotel h
            LEFT JOIN room r_inner ON h.hotel_id = r_inner.hotel_id
            GROUP BY h.hotel_id
        )
        SELECT 
            r.room_id,
            r.room_number,
            r.price,
            r.capacity,
            r.view_type,
            r.is_extendable,
            h.address AS hotel_address,
            h.area,
            h.category,
            hc.name AS hotel_chain,
            hrc.room_count
        FROM room r
        JOIN hotel h ON r.hotel_id = h.hotel_id
        JOIN hotel_chain hc ON h.chain_id = hc.chain_id
        JOIN hotel_room_counts hrc ON h.hotel_id = hrc.hotel_id
        WHERE 
            r.room_id NOT IN (
                SELECT b.room_id
                FROM booking b
                WHERE (b.in_date, b.out_date) OVERLAPS ('{in_date}'::date, '{out_date}'::date)
            )
            {where_clause}
        ORDER BY r.price;
    """

def build_room_search_query(filters):
    sql = f"""
        SELECT r.*, h.category, h.area, hc.name as chain_name
        FROM room r
        JOIN hotel h ON r.hotel_id = h.hotel_id
        JOIN hotel_chain hc ON h.chain_id = hc.chain_id
        WHERE NOT EXISTS (
            SELECT 1 FROM booking b
            WHERE b.room_id = r.room_id
              AND b.in_date < '{filters['checkout']}' AND b.out_date > '{filters['checkin']}'
        )
        AND NOT EXISTS (
            SELECT 1 FROM rental rt
            WHERE rt.room_id = r.room_id
              AND rt.in_date < '{filters['checkout']}' AND rt.out_date > '{filters['checkin']}'
        )
    """

    if filters.get("hotel_chains"):
        ids = ','.join(str(cid) for cid in filters['hotel_chains'])
        sql += f" AND hc.chain_id IN ({ids})"

    if filters.get("capacity"):
        sql += f" AND r.capacity >= {filters['capacity']}"

    if filters.get("category") and filters['category'] != 0:
        sql += f" AND h.category = {filters['category']}"

    if filters.get("area"):
        sql += f" AND h.area = '{filters['area']}'"

    if filters.get("min_price"):
        sql += f" AND r.price >= {filters['min_price']}"

    if filters.get("max_price"):
        sql += f" AND r.price <= {filters['max_price']}"

    if filters.get("min_rooms"):
        sql += f" AND h.hotel_id IN (SELECT hotel_id FROM room GROUP BY hotel_id HAVING COUNT(*) >= {filters['min_rooms']})"

    if filters.get("max_rooms"):
        sql += f" AND h.hotel_id IN (SELECT hotel_id FROM room GROUP BY hotel_id HAVING COUNT(*) <= {filters['max_rooms']})"

    return sql