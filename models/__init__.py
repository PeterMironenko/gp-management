from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from models.user import UserModel
from models.staff import StaffModel
from models.patient import PatientModel