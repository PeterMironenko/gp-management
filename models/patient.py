from flask_sqlalchemy import SQLAlchemy
from models import db

class PatientModel(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), unique=False, nullable=False)
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
    created_at = db.Column(db.DateTime, unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, unique=False, nullable=False)
    appointments = db.relationship("AppointmentModel", back_populates="patient", cascade="all, delete-orphan")
    drugs = db.relationship("DrugModel", back_populates="patient", cascade="all, delete-orphan")
    lab_records = db.relationship("LabRecordModel", back_populates="patient", cascade="all, delete-orphan")
    medical_information = db.relationship("MedicalInformationModel", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    medications = db.relationship("MedicationModel", back_populates="patient", cascade="all, delete-orphan")
    staff = db.relationship("StaffModel", back_populates="patients")

    def json(self):
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'landline_phone': self.landline_phone,
            'mobile_phone': self.mobile_phone,
            'email': self.email,
            'address_street': self.address_street,
            'address_city': self.address_city,
            'address_county': self.address_county,
            'address_postcode': self.address_postcode,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def find_by_username(cls, first_name, last_name, date_of_birth):
        return cls.query.filter_by(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth
        ).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
