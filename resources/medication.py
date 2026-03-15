from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import MedicationModel, db
from schemas import MedicationSchema


blp = Blueprint("Medications", __name__, description="Operations on medications")


@blp.route("/medication")
class MedicationList(MethodView):
    @blp.response(200, MedicationSchema(many=True))
    def get(self):
        patient_id = request.args.get("patient_id", type=int)
        query = MedicationModel.query
        if patient_id is not None:
            query = query.filter_by(patient_id=patient_id)
        return query.order_by(MedicationModel.id.asc()).all()

    @blp.arguments(MedicationSchema)
    @blp.response(201, MedicationSchema)
    def post(self, medication_data):
        medication = MedicationModel(**medication_data)
        try:
            db.session.add(medication)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating medication.")
        return medication, 201


@blp.route("/medication/<int:medication_id>")
class Medication(MethodView):
    @blp.response(200, MedicationSchema)
    def get(self, medication_id):
        medication = db.session.get(MedicationModel, medication_id)
        if medication is None:
            abort(404, message="Medication not found")
        return medication

    @blp.arguments(MedicationSchema)
    @blp.response(200, MedicationSchema)
    def put(self, medication_data, medication_id):
        medication = db.session.get(MedicationModel, medication_id)
        if medication is None:
            abort(404, message="Medication not found")

        medication.patient_id = medication_data["patient_id"]
        medication.staff_id = medication_data.get("staff_id")
        medication.drug_id = medication_data.get("drug_id")
        medication.dosage = medication_data["dosage"]
        medication.frequency = medication_data["frequency"]
        medication.route = medication_data.get("route")
        medication.start_date = medication_data["start_date"]
        medication.end_date = medication_data.get("end_date")
        medication.notes = medication_data.get("notes")
        medication.is_approved = medication_data.get("is_approved", medication.is_approved)

        try:
            db.session.add(medication)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating medication.")
        return medication

    def delete(self, medication_id):
        medication = db.session.get(MedicationModel, medication_id)
        if medication is None:
            abort(404, message="Medication not found")

        try:
            db.session.delete(medication)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting medication.")
        return {"message": "Medication deleted."}, 200
