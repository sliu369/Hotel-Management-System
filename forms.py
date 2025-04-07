from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SelectMultipleField, IntegerField, DecimalField, SubmitField, widgets, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange, Email
from wtforms.widgets import ListWidget, Select
from wtforms.validators import Email


class CustomerSearchForm(FlaskForm):
    first_name = StringField("First Name", validators=[Optional()])
    last_name = StringField("Last Name", validators=[Optional()])
    submit = SubmitField("Search")

class CustomerAddForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    type_of_id = StringField("Type of ID", validators=[DataRequired()])
    submit = SubmitField("Add Customer")

class PhoneNumberForm(FlaskForm):
    class Meta:
        csrf = False
    phone = StringField("Phone Number", validators=[Optional()])

class HotelAddForm(FlaskForm):
    chain_id = SelectField("Hotel Chain", choices=[], coerce=int, validators=[DataRequired()])
    hotel_email = StringField("Hotel Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[DataRequired()])
    area = StringField("Area", validators=[DataRequired()])
    category = IntegerField("Category (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    phone_numbers = FieldList(FormField(PhoneNumberForm), min_entries=3)
    manager_sin = StringField("Manager SIN", validators=[DataRequired()])
    manager_first_name = StringField("Manager First Name", validators=[DataRequired()])
    manager_last_name = StringField("Manager Last Name", validators=[DataRequired()])
    submit = SubmitField("Add Hotel")

class RoleForm(FlaskForm):
    class Meta:
        csrf = False
    role = StringField("Role", validators=[Optional()])

class EmployeeAddForm(FlaskForm):
    hotel_id = SelectField("Hotel", coerce=int, validators=[DataRequired()])
    sin_number = StringField("SIN Number", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    roles = FieldList(FormField(RoleForm), min_entries=2)
    submit = SubmitField("Add Employee")

class AmenityForm(FlaskForm):
    class Meta:
        csrf = False
    amenity = StringField("Amenity", validators=[Optional()])

class ProblemForm(FlaskForm):
    class Meta:
        csrf = False
    problem = StringField("Problem", validators=[Optional()])

class RoomAddForm(FlaskForm):
    hotel_id = SelectField("Hotel", coerce=int, validators=[DataRequired()])
    room_number = StringField("Room Number", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired()])
    view_type = SelectField("View Type", choices=[("", "None"), ("sea view", "Sea View"), ("mountain view", "Mountain View")], validators=[Optional()])
    is_extendable = BooleanField("Is Extendable")
    amenities = FieldList(FormField(AmenityForm), min_entries=3)
    problems = FieldList(FormField(ProblemForm), min_entries=2)
    submit = SubmitField("Add Room")

class RoomSearchForm(FlaskForm):
    hotel_chains = SelectMultipleField("Hotel Chains", coerce=int, validators=[Optional()])
    checkin = DateField("Check-in", validators=[DataRequired()])
    checkout = DateField("Check-out", validators=[DataRequired()])
    capacity = IntegerField("Capacity", default=1, validators=[Optional()])
    category = SelectField("Category", coerce=int, choices=[(0, "Any")] + [(i, f"{i} star") for i in range(1, 6)], validators=[Optional()])
    area = SelectField("Area", validators=[Optional()])
    min_rooms = IntegerField("Min Rooms", validators=[Optional()])
    max_rooms = IntegerField("Max Rooms", validators=[Optional()])
    min_price = DecimalField("Min Price", validators=[Optional()])
    max_price = DecimalField("Max Price", validators=[Optional()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Search")

class BookingToRentalForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    type_of_id = StringField("Type of ID", validators=[DataRequired()])
    employee_id = IntegerField("Employee ID", validators=[DataRequired()])
    submit = SubmitField("Search Bookings")

class DirectRentalForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    type_of_id = StringField("Type of ID", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])

    checkin = DateField("Check-in Date", validators=[DataRequired()])
    checkout = DateField("Check-out Date", validators=[DataRequired()])

    capacity = IntegerField("Minimum Capacity", default=1, validators=[Optional(), NumberRange(min=1)])
    min_price = DecimalField("Min Price", validators=[Optional(), NumberRange(min=0)])
    max_price = DecimalField("Max Price", validators=[Optional(), NumberRange(min=0)])

    employee_id = IntegerField("Employee ID", validators=[DataRequired()])

    submit = SubmitField("Search Available Rooms")

class SelectHotelForm(FlaskForm):
    hotel_id = SelectField("Select Hotel", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Get Capacity")
