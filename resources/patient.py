from http import HTTPStatus
from datetime import datetime

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import db, PatientModel
from schemas import PatientSchema, PatientUpdateSchema

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

    @blp.arguments(PatientUpdateSchema)
    @blp.response(HTTPStatus.OK, PatientSchema)
    def put(self, patient_data, patient_id):
        patient = db.session.get(PatientModel, patient_id)
        if patient:
            for key, value in patient_data.items():
                setattr(patient, key, value)
            patient.updated_at = datetime.now()
        else:
            required_fields = [
                "staff_id",
                "first_name",
                "last_name",
                "date_of_birth",
                "landline_phone",
                "mobile_phone",
                "email",
                "address_street",
                "address_city",
                "address_county",
                "address_postcode",
                "emergency_contact_name",
                "emergency_contact_phone",
            ]
            missing_fields = [field for field in required_fields if field not in patient_data]
            if missing_fields:
                abort(
                    HTTPStatus.BAD_REQUEST,
                    message=f"Missing required fields for new patient: {', '.join(missing_fields)}",
                )
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
