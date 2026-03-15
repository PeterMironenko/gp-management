from flask_sqlalchemy import SQLAlchemy
from models import db

class PatientModel(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), unique=False, nullable=False)
    last_name = db.Column(db.String(30), unique=False, nullable=False)
    date_of_birth = db.Column(db.Date, unique=False, nullable=False)
    landline_phone = db.Column(db.String(15), unique=True, nullable=False)
    mobile_phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    address_street = db.Column(db.String(200), unique=False, nullable=False)
    address_city = db.Column(db.String(100), unique=False, nullable=False)
    address_county = db.Column(db.String(100), unique=False, nullable=False)
    address_postcode = db.Column(db.String(20), unique=False, nullable=False)
    emergency_contact_name = db.Column(db.String(60), unique=False, nullable=False)
    emergency_contact_phone = db.Column(db.String(15), unique=False, nullable=False)
    crreated_at = db.Column(db.DateTime, unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    
