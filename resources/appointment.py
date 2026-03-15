from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import AppointmentModel, db
from schemas import AppointmentSchema


blp = Blueprint("Appointments", __name__, description="Operations on appointments")


@blp.route("/appointment")
class AppointmentList(MethodView):
    @blp.response(200, AppointmentSchema(many=True))
    def get(self):
        patient_id = request.args.get("patient_id", type=int)
        query = AppointmentModel.query
        if patient_id is not None:
            query = query.filter_by(patient_id=patient_id)
        return query.order_by(AppointmentModel.appointment_date.asc()).all()

    @blp.arguments(AppointmentSchema)
    @blp.response(201, AppointmentSchema)
    def post(self, appointment_data):
        appointment = AppointmentModel(**appointment_data)
        try:
            db.session.add(appointment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the appointment.")
        return appointment, 201


@blp.route("/appointment/<int:appointment_id>")
class Appointment(MethodView):
    @blp.response(200, AppointmentSchema)
    def get(self, appointment_id):
        appointment = db.session.get(AppointmentModel, appointment_id)
        if appointment is None:
            abort(404, message="Appointment not found")
        return appointment

    @blp.arguments(AppointmentSchema)
    @blp.response(200, AppointmentSchema)
    def put(self, appointment_data, appointment_id):
        appointment = db.session.get(AppointmentModel, appointment_id)
        if appointment is None:
            abort(404, message="Appointment not found")

        appointment.patient_id = appointment_data["patient_id"]
        appointment.staff_id = appointment_data["staff_id"]
        appointment.appointment_date = appointment_data["appointment_date"]
        appointment.duration_minutes = appointment_data["duration_minutes"]
        appointment.reason = appointment_data["reason"]
        appointment.notes = appointment_data.get("notes")
        appointment.location = appointment_data.get("location")

        try:
            db.session.add(appointment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the appointment.")

        return appointment

    def delete(self, appointment_id):
        appointment = db.session.get(AppointmentModel, appointment_id)
        if appointment is None:
            abort(404, message="Appointment not found")

        try:
            db.session.delete(appointment)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the appointment.")

        return {"message": "Appointment deleted."}, 200
