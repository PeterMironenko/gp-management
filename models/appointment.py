from models import db
from models.patient import PatientModel

class AppointmentModel(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), unique=False, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), unique=False, nullable=False)
    appointment_date = db.Column(db.DateTime, unique=False, nullable=False)
    duration_minutes = db.Column(db.Integer, unique=False, nullable=False)
    reason = db.Column(db.String(255), unique=False, nullable=False)
    notes = db.Column(db.Text, unique=False, nullable=True)
    location = db.Column(db.String(255), unique=False, nullable=True)
    patient = db.relationship("PatientModel", back_populates="appointments")
    staff = db.relationship("StaffModel", back_populates="appointments")
    

    def json(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'staff_id': self.staff_id,
            'appointment_date': self.appointment_date,
            'duration_minutes': self.duration_minutes,
            'reason': self.reason,
            'notes': self.notes,
            'location': self.location
        }

    @classmethod
    def find_by_username(cls, patient_first_name, patient_last_name):
        return cls.query.join(PatientModel).filter(
            PatientModel.first_name == patient_first_name,
            PatientModel.last_name == patient_last_name
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



