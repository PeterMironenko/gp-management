from models import db
from models.patient import PatientModel

class MedicationModel(db.Model):
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), unique=False, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), unique=False, nullable=True)
    drug_id = db.Column(db.Integer, unique=False, nullable=True)
    dosage = db.Column(db.String(255), unique=False, nullable=False)
    frequency = db.Column(db.String(255), unique=False, nullable=False)
    route = db.Column(db.String(255), unique=False, nullable=True)
    start_date = db.Column(db.Date, unique=False, nullable=False)
    end_date = db.Column(db.Date, unique=False, nullable=True)
    notes = db.Column(db.Text, unique=False, nullable=True)
    is_approved = db.Column(db.Boolean, unique=False, nullable=True, default=False)

    patient = db.relationship("PatientModel", back_populates="medications")

    def json(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'staff_id': self.staff_id,
            'drug_id': self.drug_id,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'route': self.route,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'notes': self.notes,
            'is_approved': self.is_approved,
        }

    @classmethod
    def find_by_patient_id(cls, patient_id):
        return cls.query.filter_by(patient_id=patient_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()