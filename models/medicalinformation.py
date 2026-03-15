from models import db
from models.patient import PatientModel

class MedicalInformationModel(db.Model):
    __tablename__ = 'medical_information'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), unique=False, nullable=False)
    primary_condition = db.Column(db.String(255), unique=False, nullable=True)
    chronicillnesses = db.Column(db.Text, unique=False, nullable=True)
    allergies = db.Column(db.Text, unique=False, nullable=True)
    surgeries = db.Column(db.Text, unique=False, nullable=True)
    immunization = db.Column(db.Text, unique=False, nullable=True)
    last_updated = db.Column(db.DateTime, unique=False, nullable=False)

    patient = db.relationship("PatientModel", back_populates="medical_information")

    def json(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'allergies': self.allergies,
            'chronicillnesses': self.chronicillnesses,
            'primary_condition': self.primary_condition,
            'surgeries': self.surgeries,
            'immunization': self.immunization,
            'last_updated': self.last_updated
        }

    @classmethod
    def find_by_patient_id(cls, patient_id):
        return cls.query.filter_by(patient_id=patient_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()