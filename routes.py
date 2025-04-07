from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date

from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from forms import CustomerSearchForm, CustomerAddForm, HotelAddForm, EmployeeAddForm, RoomAddForm, RoomSearchForm, BookingToRentalForm, DirectRentalForm, SelectHotelForm
from db.queries import build_room_search_query


db = SQLAlchemy()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY 

db.init_app(app) 


@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")


# process rentals without a booking
@app.route("/direct-rental", methods=["GET", "POST"])
def direct_rental():
    form = DirectRentalForm()
    rooms = []
    nights = 0

    # searches for all the rooms in the employee's hotel and according to filters
    if form.validate_on_submit():
        fname = form.first_name.data.strip()
        lname = form.last_name.data.strip()
        type_of_id = form.type_of_id.data.strip()
        address = form.address.data.strip()
        checkin = form.checkin.data
        checkout = form.checkout.data
        emp_id = form.employee_id.data
        capacity = form.capacity.data or 1
        min_price = form.min_price.data
        max_price = form.max_price.data

        nights = (checkout - checkin).days
        with db.engine.begin() as conn:
            hotel_id = conn.execute(text("SELECT hotel_id FROM employee WHERE employee_id = :eid"), {"eid": emp_id}).scalar()
            if not hotel_id:
                flash("Invalid employee ID.", "danger")
                return redirect(url_for("direct_rental"))
            # 
            sql_query = """
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
            """
            params = {
                "hid": hotel_id,
                "cap": capacity,
                "checkin": checkin,
                "checkout": checkout
            }

            if min_price is not None:
                sql_query += " AND r.price >= :min_price"
                params["min_price"] = min_price
            if max_price is not None:
                sql_query += " AND r.price <= :max_price"
                params["max_price"] = max_price

            rows = conn.execute(text(sql_query), params).mappings().all()

            amenity_map = {}
            problem_map = {}
            if rows:
                room_ids = [r["room_id"] for r in rows]

                amenity_rows = conn.execute(text("""
                    SELECT room_id, amenity FROM room_amenities
                    WHERE room_id = ANY(:ids)
                """), {"ids": room_ids}).mappings().all()
                for row in amenity_rows:
                    amenity_map.setdefault(row.room_id, []).append(row.amenity)

                problem_rows = conn.execute(text("""
                    SELECT room_id, problem_description FROM room_problems
                    WHERE room_id = ANY(:ids)
                """), {"ids": room_ids}).mappings().all()
                for row in problem_rows:
                    problem_map.setdefault(row.room_id, []).append(row.problem_description)

            for room in rows:
                room = dict(room)
                room["amenities"] = amenity_map.get(room["room_id"], [])
                room["problems"] = problem_map.get(room["room_id"], [])
                room["rental_price"] = float(room["price"]) * nights
                rooms.append(room)

    # if employee selected the booking for the customer
    elif request.method == "POST" and 'confirm_room_id' in request.form:
        room_id = int(request.form['confirm_room_id'])
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        fname = request.form['first_name'].strip()
        lname = request.form['last_name'].strip()
        address = request.form['address'].strip()
        type_of_id = request.form['type_of_id'].strip()
        emp_id = int(request.form['employee_id'])
        payment_input = float(request.form.get('payment_amount', 0))
        price = float(request.form.get('rental_price', 0))

        with db.engine.begin() as conn:
            emp_check = conn.execute(text("SELECT hotel_id FROM employee WHERE employee_id = :eid"), {"eid": emp_id}).scalar()
            if not emp_check:
                flash("Invalid employee ID.", "danger")
                return redirect(url_for("direct_rental"))

            result = conn.execute(text("""
                SELECT customer_id, type_of_id FROM customer
                WHERE first_name = :fname AND last_name = :lname AND address = :addr
            """), {
                "fname": fname,
                "lname": lname,
                "addr": address
            })
            row = result.first()
            if row: # if customer exits, we ask for id and update it, or add it if they never did a rental before
                customer_id = row.customer_id
                if row.type_of_id != type_of_id:
                    conn.execute(text("""
                        UPDATE customer SET type_of_id = :tid WHERE customer_id = :cid
                    """), {"tid": type_of_id, "cid": customer_id})
            else: # if customer doesnt exist in the db
                result = conn.execute(text("SELECT MAX(customer_id) FROM customer"))
                customer_id = (result.scalar() or 0) + 1
                conn.execute(text("""
                    INSERT INTO customer (customer_id, first_name, last_name, address, registration_date, type_of_id)
                    VALUES (:id, :fname, :lname, :addr, :reg, :tid)
                """), {
                    "id": customer_id,
                    "fname": fname,
                    "lname": lname,
                    "addr": address,
                    "reg": date.today(),
                    "tid": type_of_id
                })

            if payment_input != price:
                flash(f"Incorrect payment amount. Expected ${price:.2f}.", "warning")
                return redirect(url_for("direct_rental"))

            result = conn.execute(text("SELECT MAX(renting_id) FROM rental"))
            next_id = (result.scalar() or 0) + 1

            result = conn.execute(text("SELECT hotel_id FROM room WHERE room_id = :rid"), {"rid": room_id})
            hotel_id = result.scalar()

            # creates rental tuple
            conn.execute(text("""
                INSERT INTO rental (renting_id, room_id, customer_id, in_date, out_date, employee_id, rental_price, hotel_id)
                VALUES (:rid, :room_id, :cust_id, :in_date, :out_date, :emp_id, :price, :hotel_id)
            """), {
                "rid": next_id,
                "room_id": room_id,
                "cust_id": customer_id,
                "in_date": checkin,
                "out_date": checkout,
                "emp_id": emp_id,
                "price": price,
                "hotel_id": hotel_id
            })

            flash("Rental confirmed!", "success")
            return redirect(url_for("direct_rental"))

    return render_template("direct-rental.html", form=form, rooms=rooms, nights=nights)


# convert booking into a rental
@app.route("/booking-to-rental", methods=["GET", "POST"])
def booking_to_rental():
    form = BookingToRentalForm()
    bookings = []

    # find all bookings that customer have made, displayed in order from most to least recent 
    if request.method == "POST" and 'booking_id' in request.form:
        booking_id = int(request.form['booking_id'])
        customer_id = int(request.form['customer_id'])
        employee_id = int(request.form['employee_id'])
        type_of_id = request.form['type_of_id'].strip()
        payment_input = float(request.form.get('payment_amount', 0))

        with db.engine.begin() as conn:
            emp_hotel = conn.execute(text("SELECT hotel_id FROM employee WHERE employee_id = :eid"), {"eid": employee_id}).scalar()
            row = conn.execute(text("""
                SELECT b.room_id, b.in_date, b.out_date, r.price, b.hotel_id
                FROM booking b
                JOIN room r ON b.room_id = r.room_id
                WHERE b.booking_id = :bid
            """), {"bid": booking_id}).first()

            if not row:
                flash("Booking not found.", "danger")
                return redirect(url_for("booking_to_rental"))

            if emp_hotel != row.hotel_id:
                flash("Cannot confirm: Employee and booking are not at the same hotel.", "danger")
                return redirect(url_for("booking_to_rental"))

            num_nights = (row.out_date - row.in_date).days
            rental_price = float(row.price) * num_nights # price will be room price * number of nights

            # if customer payment doesn't match the rental price
            if payment_input != rental_price:
                flash(f"Incorrect payment amount. Expected ${rental_price:.2f}.", "warning")
                return redirect(url_for("booking_to_rental"))

            result = conn.execute(text("SELECT MAX(renting_id) FROM rental"))
            next_rental_id = (result.scalar() or 0) + 1

            # creates the rental tuple
            conn.execute(text("""
                INSERT INTO rental (renting_id, room_id, customer_id, in_date, out_date, employee_id, booking_id, rental_price, hotel_id)
                VALUES (:rid, :room_id, :cust_id, :in_date, :out_date, :emp_id, :book_id, :price, :hotel_id)
            """), {
                "rid": next_rental_id,
                "room_id": row.room_id,
                "cust_id": customer_id,
                "in_date": row.in_date,
                "out_date": row.out_date,
                "emp_id": employee_id,
                "book_id": booking_id,
                "price": rental_price,
                "hotel_id": row.hotel_id
            })

            conn.execute(text("""
                UPDATE customer SET type_of_id = :idtype WHERE customer_id = :cid
            """), {"idtype": type_of_id, "cid": customer_id})

            # deletes booking
            # conn.execute(text("DELETE FROM booking WHERE booking_id = :bid"), {"bid": booking_id})

            flash("Rental confirmed and customer ID type updated.", "success")
            return redirect(url_for("booking_to_rental"))

    elif form.validate_on_submit():
        fname = (form.first_name.data or "").strip()
        lname = (form.last_name.data or "").strip()
        addr = (form.address.data or "").strip()

        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT customer_id FROM customer
                WHERE first_name = :fname AND last_name = :lname AND address = :addr
            """), {"fname": fname, "lname": lname, "addr": addr})
            row = result.first()
            if row:
                customer_id = row.customer_id
                rows = conn.execute(text("""
                    SELECT b.*, r.price, h.area, h.hotel_email, h.address
                    FROM booking b
                    JOIN room r ON b.room_id = r.room_id
                    JOIN hotel h ON b.hotel_id = h.hotel_id
                    WHERE b.customer_id = :cid
                    ORDER BY b.in_date DESC
                """), {"cid": customer_id}).mappings().all()
                bookings = []

                for row in rows:
                    b = dict(row)  # convert to regular dict
                    nights = (b["out_date"] - b["in_date"]).days
                    b["rental_price"] = float(b["price"]) * nights
                    bookings.append(b)
            else:
                flash("Customer not found.", "danger")

    return render_template("booking-to-rental.html", form=form, bookings=bookings)


# customer can book a room
@app.route('/room-search', methods=['GET', 'POST'])
def room_search():
    form = RoomSearchForm()
    rooms = []
    selected_room = request.args.get("selected")

    # find the 5 hotel chains
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT chain_id, name FROM hotel_chain ORDER BY name"))
        form.hotel_chains.choices = [(row.chain_id, row.name) for row in result]

        result = conn.execute(text("SELECT DISTINCT area FROM hotel ORDER BY area"))
        form.area.choices = [("", "Any")] + [(row.area, row.area) for row in result]

        # search for rooms according to our filters
        if form.validate_on_submit():
            filters = {
                "checkin": form.checkin.data,
                "checkout": form.checkout.data,
                "hotel_chains": form.hotel_chains.data,
                "capacity": form.capacity.data,
                "category": form.category.data,
                "area": form.area.data,
                "min_rooms": form.min_rooms.data,
                "max_rooms": form.max_rooms.data,
                "min_price": form.min_price.data,
                "max_price": form.max_price.data
            }

            # build_room_search_query is our filters
            sql = build_room_search_query(filters)
            rooms = [dict(row) for row in conn.execute(text(sql)).mappings().all()]

            # display all amenities, problems and hotel address
            room_ids = [r['room_id'] for r in rooms]
            if room_ids:
                amenity_rows = conn.execute(text("""
                    SELECT room_id, amenity FROM room_amenities
                    WHERE room_id = ANY(:ids)
                """), {"ids": room_ids}).mappings().all()

                problem_rows = conn.execute(text("""
                    SELECT room_id, problem_description FROM room_problems
                    WHERE room_id = ANY(:ids)
                """), {"ids": room_ids}).mappings().all()

                address_rows = conn.execute(text("""
                    SELECT r.room_id, h.address
                    FROM room r
                    JOIN hotel h ON r.hotel_id = h.hotel_id
                    WHERE r.room_id = ANY(:ids)
                """), {"ids": room_ids}).mappings().all()
                address_map = {r.room_id: r.address for r in address_rows}

                for room in rooms:
                    room['amenities'] = [a['amenity'] for a in amenity_rows if a['room_id'] == room['room_id']]
                    room['problems'] = [p['problem_description'] for p in problem_rows if p['room_id'] == room['room_id']]
                    room['address'] = address_map.get(room['room_id'])

        # customer confirms booking
        elif request.method == 'POST' and 'confirm_room_id' in request.form:
            room_id = int(request.form['confirm_room_id'])
            checkin = request.form['checkin']
            checkout = request.form['checkout']
            fname = request.form['first_name'].strip()
            lname = request.form['last_name'].strip()
            addr = request.form['address'].strip()

            with db.engine.begin() as tx:
                result = tx.execute(text("""
                    SELECT customer_id FROM customer
                    WHERE first_name = :fname AND last_name = :lname AND address = :addr
                """), {"fname": fname, "lname": lname, "addr": addr})
                row = result.first()

                # if customer exists in our db
                if row:
                    customer_id = row.customer_id
                else: # we create a new customer tuple. We don't ask for type of id as it's gonna be filled in when customer gets their booking transformed into a rental
                    result = tx.execute(text("SELECT MAX(customer_id) FROM customer"))
                    customer_id = (result.scalar() or 0) + 1
                    tx.execute(text("""
                        INSERT INTO customer (customer_id, first_name, last_name, address, registration_date)
                        VALUES (:id, :fname, :lname, :addr, :reg)
                    """), {
                        "id": customer_id,
                        "fname": fname,
                        "lname": lname,
                        "addr": addr,
                        "reg": date.today()
                    })

                result = tx.execute(text("""
                    SELECT hotel_id FROM room WHERE room_id = :rid
                """), {"rid": room_id})
                hotel_id = result.scalar()

                result = tx.execute(text("SELECT MAX(booking_id) FROM booking"))
                next_booking_id = (result.scalar() or 0) + 1

                # create booking
                tx.execute(text("""
                    INSERT INTO booking (booking_id, room_id, customer_id, in_date, out_date, hotel_id)
                    VALUES (:bid, :rid, :cid, :in_date, :out_date, :hid)
                """), {
                    "bid": next_booking_id,
                    "rid": room_id,
                    "cid": customer_id,
                    "in_date": checkin,
                    "out_date": checkout,
                    "hid": hotel_id
                })

            # if booking is succesful
            flash("Booking successful!", "success")
            return redirect(url_for('room_search'))

    return render_template("room-search.html", form=form, rooms=rooms, selected_room=selected_room)


# view 2
@app.route('/capacity-per-hotel', methods=["GET", "POST"])
def view_two():
    form = SelectHotelForm()
    total_capacity = None

    with db.engine.connect() as conn:
        hotels = conn.execute(text("""
            SELECT h.hotel_id, hc.name || ' | ' || h.area || ' | ' || h.address AS label
            FROM hotel h
            JOIN hotel_chain hc ON h.chain_id = hc.chain_id
            ORDER BY hc.name, h.area
        """)).fetchall()
        form.hotel_id.choices = [(row.hotel_id, row.label) for row in hotels]

        if form.validate_on_submit():
            selected_id = form.hotel_id.data
            result = conn.execute(text("SELECT total_room_capacity FROM Hotel_Aggregated_Capacity WHERE hotel_id = :hid"), {"hid": selected_id}).scalar()
            total_capacity = result

    return render_template("capacity-per-hotel.html", form=form, total_capacity=total_capacity)


# view 1
@app.route('/room-per-area')
def view_one():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM view_one")).mappings().all()
        areas = [dict(row) for row in result]
    return render_template("room-per-area.html", areas=areas)


# update/delete/edit customer
@app.route('/manage-customer', methods=['GET', 'POST'])
def manage_customer():

    search_form = CustomerSearchForm(request.args)
    add_form = CustomerAddForm()
    edit_id = request.args.get('edit_id')  # which customer is in edit mode
    customers = []

    # delete customer
    if request.method == 'POST' and 'delete_id' in request.form:
        with db.engine.begin() as conn:
            conn.execute(text("DELETE FROM Customer WHERE customer_ID = :id"),
                         {"id": request.form['delete_id']})
        return redirect(url_for('manage_customer'))

    # edit customer
    if request.method == 'POST' and 'edit_id' in request.form:
        with db.engine.begin() as conn:
            conn.execute(text("""
                UPDATE Customer
                SET first_name = :first_name,
                    last_name = :last_name,
                    address = :address,
                    type_of_id = :type_of_id
                WHERE customer_ID = :id
            """), {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "address": request.form["address"],
                "type_of_id": request.form["type_of_id"],
                "id": request.form["edit_id"]
            })
        return redirect(url_for('manage_customer'))
    
    # add customer
    if request.method == 'POST' and add_form.submit.data:
        with db.engine.begin() as conn:
            result = conn.execute(text("SELECT MAX(customer_id) FROM customer"))
            next_id = (result.scalar() or 0) + 1

            conn.execute(text("""
                INSERT INTO customer (customer_id, first_name, last_name, address, registration_date, type_of_id)
                VALUES (:id, :first_name, :last_name, :address, :reg_date, :type_of_id)
                """), {
                "id": next_id,
                "first_name": add_form.first_name.data,
                "last_name": add_form.last_name.data,
                "address": add_form.address.data,
                "reg_date": date.today(),
                "type_of_id": add_form.type_of_id.data
            })
        return redirect(url_for('manage_customer'))

    # show all customers
    with db.engine.connect() as conn:
        sql = "SELECT * FROM Customer WHERE 1=1"
        params = {}
        if search_form.first_name.data:
            sql += " AND first_name ILIKE :first_name"
            params['first_name'] = f"%{search_form.first_name.data}%"
        if search_form.last_name.data:
            sql += " AND last_name ILIKE :last_name"
            params['last_name'] = f"%{search_form.last_name.data}%"

        customers = conn.execute(text(sql), params).mappings().all()

    return render_template(
        'manage-customer.html',
        search_form=search_form,
        add_form=add_form,
        customers=customers,
        edit_id=edit_id
    )


# update/delete/edit room
@app.route('/manage-room', methods=['GET', 'POST'])
def manage_room():
    form = RoomAddForm()
    edit_id = request.args.get("edit_id")
    hotel_filter = request.args.get("hotel_filter")

    # get all the hotels
    with db.engine.connect() as conn:
        hotels = conn.execute(text("""
            SELECT h.hotel_id, hc.name AS chain_name, h.area, h.address
            FROM hotel h JOIN hotel_chain hc ON h.chain_id = hc.chain_id
            ORDER BY hc.name, h.area, h.address
        """))
        hotel_choices = [(row.hotel_id, f"{row.chain_name} {row.area} {row.address} (ID: {row.hotel_id})") for row in hotels]
        form.hotel_id.choices = hotel_choices

    # delete room
    if request.method == 'POST' and 'delete_id' in request.form:
        room_id = int(request.form['delete_id'])
        with db.engine.begin() as conn:
            conn.execute(text("DELETE FROM room WHERE room_id = :id"), {"id": room_id})
        return redirect(url_for('manage_room'))

    # edit room
    if request.method == 'POST' and 'edit_id' in request.form:
        room_id = int(request.form['edit_id'])
        with db.engine.begin() as conn:
            conn.execute(text("""
                UPDATE room
                SET hotel_id = :hotel_id, room_number = :room_number, price = :price,
                    capacity = :capacity, view_type = :view_type, is_extendable = :is_extendable
                WHERE room_id = :id
            """), {
                "hotel_id": request.form['hotel_id'],
                "room_number": request.form['room_number'],
                "price": request.form['price'],
                "capacity": request.form['capacity'],
                "view_type": request.form['view_type'] or None,
                "is_extendable": 'is_extendable' in request.form,
                "id": room_id
            })

            # 
            conn.execute(text("DELETE FROM room_amenities WHERE room_id = :id"), {"id": room_id})
            conn.execute(text("DELETE FROM room_problems WHERE room_id = :id"), {"id": room_id})

            for key in request.form:
                if key.startswith("amenity_"):
                    value = request.form[key].strip()
                    if value:
                        conn.execute(text("INSERT INTO room_amenities (room_id, amenity) VALUES (:id, :val)"), {"id": room_id, "val": value})
                elif key.startswith("problem_"):
                    value = request.form[key].strip()
                    if value:
                        conn.execute(text("INSERT INTO room_problems (room_id, problem_description) VALUES (:id, :val)"), {"id": room_id, "val": value})

        return redirect(url_for('manage_room'))

    # create room
    if form.validate_on_submit():
        with db.engine.begin() as conn:
            result = conn.execute(text("SELECT MAX(room_id) FROM room"))
            next_id = (result.scalar() or 0) + 1

            conn.execute(text("""
                INSERT INTO room (room_id, hotel_id, room_number, price, capacity, view_type, is_extendable)
                VALUES (:room_id, :hotel_id, :room_number, :price, :capacity, :view_type, :is_extendable)
            """), {
                "room_id": next_id,
                "hotel_id": form.hotel_id.data,
                "room_number": form.room_number.data,
                "price": form.price.data,
                "capacity": form.capacity.data,
                "view_type": form.view_type.data or None,
                "is_extendable": form.is_extendable.data
            })

            for a in form.amenities.entries:
                val = a.form.amenity.data
                if val:
                    conn.execute(text("INSERT INTO room_amenities (room_id, amenity) VALUES (:room_id, :val)"), {"room_id": next_id, "val": val})

            for p in form.problems.entries:
                val = p.form.problem.data
                if val:
                    conn.execute(text("INSERT INTO room_problems (room_id, problem_description) VALUES (:room_id, :val)"), {"room_id": next_id, "val": val})

        return redirect(url_for('manage_room'))

    # get all rooms 
    with db.engine.connect() as conn:
        sql_query = """
            SELECT r.*, hc.name AS chain_name, h.area, h.address
            FROM room r
            JOIN hotel h ON r.hotel_id = h.hotel_id
            JOIN hotel_chain hc ON h.chain_id = hc.chain_id
        """
        if hotel_filter:
            sql_query += " WHERE r.hotel_id = :hid"
            result = conn.execute(text(sql_query), {"hid": hotel_filter})
        else:
            result = conn.execute(text(sql_query))

        rooms = [dict(row) for row in result.mappings().all()]

        amens = conn.execute(text("SELECT * FROM room_amenities")).mappings().all()
        probs = conn.execute(text("SELECT * FROM room_problems")).mappings().all()

    amen_map = {}
    for row in amens:
        amen_map.setdefault(row.room_id, []).append(row.amenity)

    prob_map = {}
    for row in probs:
        prob_map.setdefault(row.room_id, []).append(row.problem_description)

    for room in rooms:
        room['amenities'] = amen_map.get(room['room_id'], [])
        room['problems'] = prob_map.get(room['room_id'], [])

    return render_template("manage-room.html", form=form, rooms=rooms, edit_id=edit_id, hotel_choices=hotel_choices, hotel_filter=hotel_filter)


# update/delete/edit hotel
@app.route('/manage-hotel', methods=['GET', 'POST'])
def manage_hotel():
    form = HotelAddForm()
    edit_id = request.args.get("edit_id")

    # get hotel chains from the db
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT chain_id, name FROM hotel_chain ORDER BY name"))
        form.chain_id.choices = [(row.chain_id, row.name) for row in result]

    # add hotel
    print("METHOD:", request.method)
    print("IS SUBMITTED:", form.is_submitted())
    print("VALIDATE:", form.validate_on_submit())
    print("ERRORS:", form.errors)
    if form.validate_on_submit():
        with db.engine.begin() as conn:
            result = conn.execute(text("SELECT MAX(hotel_id) FROM hotel"))
            next_id = (result.scalar() or 0) + 1

            conn.execute(text("""
                INSERT INTO hotel (hotel_id, chain_id, hotel_email, address, area, category)
                VALUES (:hotel_id, :chain_id, :hotel_email, :address, :area, :category)
            """), {
                "hotel_id": next_id,
                "chain_id": form.chain_id.data,
                "hotel_email": form.hotel_email.data,
                "address": form.address.data,
                "area": form.area.data,
                "category": form.category.data
            })

            for phone_form in form.phone_numbers.entries:
                phone = phone_form.form.phone.data
                if phone:
                    conn.execute(text("""
                        INSERT INTO hotel_phone (hotel_id, hotel_phone_num)
                        VALUES (:hotel_id, :phone)
                    """), {"hotel_id": next_id, "phone": phone})

            # create manager
            result = conn.execute(text("SELECT MAX(employee_id) FROM employee"))
            new_emp_id = (result.scalar() or 0) + 1

            conn.execute(text("""
                INSERT INTO employee (employee_id, hotel_id, sin_number, first_name, last_name)
                VALUES (:employee_id, :hotel_id, :sin_number, :first_name, :last_name)
            """), {
                "employee_id": new_emp_id,
                "hotel_id": next_id,
                "sin_number": form.manager_sin.data,
                "first_name": form.manager_first_name.data,
                "last_name": form.manager_last_name.data
            })

            conn.execute(text("""
                INSERT INTO employee_role (employee_id, role)
                VALUES (:employee_id, 'manager')
            """), {"employee_id": new_emp_id})

        return redirect(url_for('manage_hotel'))

    # delete hotel
    if request.method == 'POST' and 'delete_id' in request.form:
        with db.engine.begin() as conn:
            conn.execute(text("DELETE FROM hotel WHERE hotel_id = :id"), {"id": request.form["delete_id"]})
        return redirect(url_for('manage_hotel'))


    # edit hotel
    if request.method == 'POST' and request.form.get("edit_id"):
        hotel_id = int(request.form["edit_id"])
        with db.engine.begin() as conn:
            conn.execute(text("""
                UPDATE hotel
                SET chain_id = :chain_id,
                    hotel_email = :hotel_email,
                    address = :address,
                    area = :area,
                    category = :category
                WHERE hotel_id = :id
            """), {
                "chain_id": request.form["chain_id"],
                "hotel_email": request.form["hotel_email"],
                "address": request.form["address"],
                "area": request.form["area"],
                "category": request.form["category"],
                "id": hotel_id
            })

            # handles updates made to phone numbers
            conn.execute(text("DELETE FROM hotel_phone WHERE hotel_id = :id"), {"id": hotel_id})

            for key in request.form:
                if key.startswith("phone_"):
                    phone = request.form[key].strip()
                    if phone:
                        conn.execute(text("""
                            INSERT INTO hotel_phone (hotel_id, hotel_phone_num)
                            VALUES (:hotel_id, :phone)
                        """), {"hotel_id": hotel_id, "phone": phone})

        return redirect(url_for('manage_hotel'))
    

    # get all the hotels
    with db.engine.connect() as conn:
        hotels = [dict(row) for row in conn.execute(text("""
            SELECT h.hotel_id, h.chain_id, hc.name AS chain_name, h.hotel_email, h.address, h.area, h.category
            FROM hotel h
            JOIN hotel_chain hc ON h.chain_id = hc.chain_id
            ORDER BY h.hotel_id
        """)).mappings().all()]

        phones = conn.execute(text("SELECT hotel_id, hotel_phone_num FROM hotel_phone")).mappings().all()
        room_counts = conn.execute(text("SELECT hotel_id, COUNT(*) AS num_rooms FROM room GROUP BY hotel_id")).mappings().all()


    # built phone maps in order to display them
    phone_map = {}
    for row in phones:
        phone_map.setdefault(row.hotel_id, []).append(row.hotel_phone_num)

    room_count_map = {row.hotel_id: row.num_rooms for row in room_counts}

    for hotel in hotels:
        hotel['phones'] = phone_map.get(hotel['hotel_id'], [])
        hotel['num_rooms'] = room_count_map.get(hotel['hotel_id'], 0)

    return render_template("manage-hotel.html", form=form, hotels=hotels, edit_id=edit_id, chain_choices=form.chain_id.choices)


# update/delete/edit employee
@app.route('/manage-employee', methods=['GET', 'POST'])
def manage_employee():
    form = EmployeeAddForm()
    edit_id = request.args.get("edit_id")
    alert_message = None

    # Load hotel dropdown choices
    with db.engine.connect() as conn:
        hotel_result = conn.execute(text("""
            SELECT h.hotel_id, hc.name AS chain_name, h.area, h.address
            FROM hotel h JOIN hotel_chain hc ON h.chain_id = hc.chain_id
            ORDER BY hc.name, h.area, h.address
        """))
        hotel_choices = [(row.hotel_id, f"{row.chain_name} {row.area} {row.address} (Hotel ID: {row.hotel_id})") for row in hotel_result]
        form.hotel_id.choices = hotel_choices

    # deleting employees
    if request.method == 'POST' and 'delete_id' in request.form:
        emp_id = int(request.form['delete_id'])
        with db.engine.begin() as conn:
            result = conn.execute(text("SELECT hotel_id FROM employee WHERE employee_id = :id"), {"id": emp_id})
            hotel_id = result.scalar()

            result = conn.execute(text("""
                SELECT COUNT(*) FROM employee e
                JOIN employee_role r ON e.employee_id = r.employee_id
                WHERE TRIM(LOWER(r.role)) = 'manager' AND e.hotel_id = :hid
            """), {"hid": hotel_id})
            manager_count = result.scalar()

            result = conn.execute(text("""
                SELECT COUNT(*) FROM employee_role
                WHERE employee_id = :id AND TRIM(LOWER(role)) = 'manager'
            """), {"id": emp_id})
            is_manager = result.scalar() > 0

            # if the manager you wanna remove is the only manager left
            if manager_count == 1 and is_manager:
                flash("Cannot remove the only manager from this hotel.", "danger")
                return redirect(url_for('manage_employee', edit_id=emp_id))

            conn.execute(text("DELETE FROM employee WHERE employee_id = :id"), {"id": emp_id})

        return redirect(url_for('manage_employee'))

    # editing employees
    if request.method == 'POST' and 'edit_id' in request.form:
        emp_id = int(request.form['edit_id'])
        with db.engine.begin() as conn:
            roles = [v.strip().lower() for k, v in request.form.items() if k.startswith('role_') and v.strip() != ''] # gets all the roles
            if 'manager' not in roles:
                result = conn.execute(text("SELECT hotel_id FROM employee WHERE employee_id = :id"), {"id": emp_id})
                hotel_id = result.scalar()
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM employee e
                    JOIN employee_role r ON e.employee_id = r.employee_id
                    WHERE TRIM(LOWER(r.role)) = 'manager' AND e.hotel_id = :hid
                """), {"hid": hotel_id})
                manager_count = result.scalar()
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM employee_role
                    WHERE employee_id = :id AND TRIM(LOWER(role)) = 'manager'
                """), {"id": emp_id})
                is_manager = result.scalar() > 0
                if manager_count == 1 and is_manager:
                    flash("Cannot remove the only manager from this hotel.", "danger")
                    return redirect(url_for('manage_employee', edit_id=emp_id))

            conn.execute(text("""
                UPDATE employee
                SET hotel_id = :hotel_id,
                    sin_number = :sin,
                    first_name = :first,
                    last_name = :last
                WHERE employee_id = :id
            """), {
                "hotel_id": request.form['hotel_id'],
                "sin": request.form['sin_number'],
                "first": request.form['first_name'],
                "last": request.form['last_name'],
                "id": emp_id
            })

            conn.execute(text("DELETE FROM employee_role WHERE employee_id = :id"), {"id": emp_id})
            for key in request.form:
                if key.startswith("role_"):
                    role = request.form[key]
                    if role:
                        role = role.strip().lower()
                        if role:
                            conn.execute(text("""
                                INSERT INTO employee_role (employee_id, role)
                                VALUES (:id, :role)
                            """), {"id": emp_id, "role": role})

        return redirect(url_for('manage_employee'))

    # creating employees
    if form.validate_on_submit():
        with db.engine.begin() as conn:
            result = conn.execute(text("SELECT MAX(employee_id) FROM employee"))
            next_id = (result.scalar() or 0) + 1

            conn.execute(text("""
                INSERT INTO employee (employee_id, hotel_id, sin_number, first_name, last_name)
                VALUES (:id, :hotel_id, :sin, :first, :last)
            """), {
                "id": next_id,
                "hotel_id": form.hotel_id.data,
                "sin": form.sin_number.data,
                "first": form.first_name.data,
                "last": form.last_name.data
            })

            for role_form in form.roles.entries:
                role = role_form.form.role.data
                if role:
                    role = role.strip().lower()
                    if role:
                        conn.execute(text("""
                            INSERT INTO employee_role (employee_id, role)
                            VALUES (:id, :role)
                        """), {"id": next_id, "role": role})

        return redirect(url_for('manage_employee'))

    # Fetch all employees and their roles
    with db.engine.connect() as conn:
        employees = [dict(row) for row in conn.execute(text("SELECT * FROM employee ORDER BY employee_id")).mappings().all()]
        roles = conn.execute(text("SELECT * FROM employee_role")).mappings().all()

    role_map = {}
    for row in roles:
        role_map.setdefault(row.employee_id, []).append(row.role)

    for emp in employees:
        emp['roles'] = role_map.get(emp['employee_id'], [])

    return render_template("manage-employee.html", form=form, employees=employees, edit_id=edit_id)



'''
@app.route('/test', methods=['GET'])
def test_query():
    with db.engine.connect() as connection: # connects to db
        result = connection.execute(text(my_test_query)) # what the db returns
    rows = []
    for row in result:
        rows.append(dict(row._mapping))
    return jsonify(rows)
'''