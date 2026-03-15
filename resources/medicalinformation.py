from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import MedicalInformationModel, db
from schemas import MedicalInformationSchema


blp = Blueprint("MedicalInformation", __name__, description="Operations on medical information")


@blp.route("/medicalinformation")
class MedicalInformationList(MethodView):
    @blp.response(200, MedicalInformationSchema(many=True))
    def get(self):
        patient_id = request.args.get("patient_id", type=int)
        query = MedicalInformationModel.query
        if patient_id is not None:
            query = query.filter_by(patient_id=patient_id)
        return query.order_by(MedicalInformationModel.id.asc()).all()

    @blp.arguments(MedicalInformationSchema)
    @blp.response(201, MedicalInformationSchema)
    def post(self, medicalinformation_data):
        medical_information = MedicalInformationModel(**medicalinformation_data)
        try:
            db.session.add(medical_information)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating medical information.")
        return medical_information, 201


@blp.route("/medicalinformation/<int:medicalinformation_id>")
class MedicalInformation(MethodView):
    @blp.response(200, MedicalInformationSchema)
    def get(self, medicalinformation_id):
        medical_information = db.session.get(MedicalInformationModel, medicalinformation_id)
        if medical_information is None:
            abort(404, message="Medical information not found")
        return medical_information

    @blp.arguments(MedicalInformationSchema)
    @blp.response(200, MedicalInformationSchema)
    def put(self, medicalinformation_data, medicalinformation_id):
        medical_information = db.session.get(MedicalInformationModel, medicalinformation_id)
        if medical_information is None:
            abort(404, message="Medical information not found")

        medical_information.patient_id = medicalinformation_data["patient_id"]
        medical_information.primary_condition = medicalinformation_data.get("primary_condition")
        medical_information.chronicillnesses = medicalinformation_data.get("chronicillnesses")
        medical_information.allergies = medicalinformation_data.get("allergies")
        medical_information.surgeries = medicalinformation_data.get("surgeries")
        medical_information.immunization = medicalinformation_data.get("immunization")
        medical_information.last_updated = medicalinformation_data["last_updated"]

        try:
            db.session.add(medical_information)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating medical information.")
        return medical_information

    def delete(self, medicalinformation_id):
        medical_information = db.session.get(MedicalInformationModel, medicalinformation_id)
        if medical_information is None:
            abort(404, message="Medical information not found")

        try:
            db.session.delete(medical_information)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting medical information.")
        return {"message": "Medical information deleted."}, 200
