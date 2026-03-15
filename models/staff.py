from models import db


class StaffModel(db.Model):
    __tablename__ = "staff"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), unique=False, nullable=False)
    last_name = db.Column(db.String(30), unique=False, nullable=False)
    date_of_birth = db.Column(db.Date, unique=False, nullable=False)
    work_phone = db.Column(db.String(15), unique=True, nullable=False)
    mobile_phone = db.Column(db.String(15), unique=True, nullable=False)
    work_email = db.Column(db.String(80), unique=True, nullable=False)
    position = db.Column(db.String(50), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    user = db.relationship("UserModel", back_populates="staff")
    patients = db.relationship("PatientModel", back_populates="staff", cascade="all, delete-orphan")
    appointments = db.relationship("AppointmentModel", back_populates="staff", cascade="all, delete-orphan")
    lab_records = db.relationship("LabRecordModel", back_populates="staff", cascade="all, delete-orphan")
