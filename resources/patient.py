from http import HTTPStatus
from datetime import datetime

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import db, PatientModel
from schemas import PatientSchema

blp = Blueprint("Patients", __name__, description="Operations on patients")


@blp.route("/patient/<int:patient_id>")
class Patient(MethodView):
    @blp.response(HTTPStatus.OK, PatientSchema)
    def get(self, patient_id):
        patient = db.session.get(PatientModel, patient_id)
        if patient is None:
            abort(HTTPStatus.NOT_FOUND, message="Patient not found")
        return patient

    def delete(self, patient_id):
        patient = db.session.get(PatientModel, patient_id)
        if patient is None:
            abort(HTTPStatus.NOT_FOUND, message="Patient not found")

        db.session.delete(patient)
        db.session.commit()
        return {"message": "Patient deleted."}, HTTPStatus.OK

    @blp.arguments(PatientSchema)
    @blp.response(HTTPStatus.OK, PatientSchema)
    def put(self, patient_data, patient_id):
        patient = db.session.get(PatientModel, patient_id)
        if patient:
            patient.staff_id = patient_data["staff_id"]
            patient.first_name = patient_data["first_name"]
            patient.last_name = patient_data["last_name"]
            patient.date_of_birth = patient_data["date_of_birth"]
            patient.landline_phone = patient_data["landline_phone"]
            patient.mobile_phone = patient_data["mobile_phone"]
            patient.email = patient_data["email"]
            patient.address_street = patient_data["address_street"]
            patient.address_city = patient_data["address_city"]
            patient.address_county = patient_data["address_county"]
            patient.address_postcode = patient_data["address_postcode"]
            patient.emergency_contact_name = patient_data["emergency_contact_name"]
            patient.emergency_contact_phone = patient_data["emergency_contact_phone"]
            patient.updated_at = datetime.now()
        else:
            now = datetime.now()
            patient = PatientModel(id=patient_id, created_at=now, updated_at=now, **patient_data)

        db.session.add(patient)
        db.session.commit()

        return patient


@blp.route("/patient")
class PatientList(MethodView):
    @blp.response(HTTPStatus.OK, PatientSchema(many=True))
    def get(self):
        staff_id = request.args.get("staff_id", type=int)
        if staff_id is not None:
            return PatientModel.query.filter_by(staff_id=staff_id).all()
        return PatientModel.query.all()

    @blp.arguments(PatientSchema)
    @blp.response(HTTPStatus.CREATED, PatientSchema)
    def post(self, patient_data):
        now = datetime.now()
        patient = PatientModel(created_at=now, updated_at=now, **patient_data)

        try:
            db.session.add(patient)
            db.session.commit()
        except SQLAlchemyError:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred while inserting the patient.")

        return patient, HTTPStatus.CREATED
