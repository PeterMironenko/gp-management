from models import db
from models.patient import PatientModel

class LabRecordModel(db.Model):
    __tablename__ = 'lab_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), unique=False, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), unique=False, nullable=False)
    test_type = db.Column(db.String(50), unique=False, nullable=False)
    test_name = db.Column(db.String(100), unique=False, nullable=False)
    test_date = db.Column(db.DateTime, unique=False, nullable=False)
    result = db.Column(db.Text, unique=False, nullable=True)
    notes = db.Column(db.Text, unique=False, nullable=True)

    patient = db.relationship("PatientModel", back_populates="lab_records")
    staff = db.relationship("StaffModel", back_populates="lab_records")

    def json(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'staff_id': self.staff_id,
            'test_name': self.test_name,
            'test_date': self.test_date,
            'result': self.result,
            'notes': self.notes
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