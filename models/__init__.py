from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from models.user import UserModel
from models.staff import StaffModel
from models.position import PositionModel
from models.patient import PatientModel
from models.appointment import AppointmentModel
from models.drug import DrugModel
from models.labrecodrds import LabRecordModel
from models.medicalinformation import MedicalInformationModel
from models.medication import MedicationModel