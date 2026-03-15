from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import LabRecordModel, db
from schemas import LabRecordSchema


blp = Blueprint("LabRecords", __name__, description="Operations on lab records")


@blp.route("/labrecord")
class LabRecordList(MethodView):
    @blp.response(200, LabRecordSchema(many=True))
    def get(self):
        patient_id = request.args.get("patient_id", type=int)
        query = LabRecordModel.query
        if patient_id is not None:
            query = query.filter_by(patient_id=patient_id)
        return query.order_by(LabRecordModel.id.asc()).all()

    @blp.arguments(LabRecordSchema)
    @blp.response(201, LabRecordSchema)
    def post(self, labrecord_data):
        labrecord = LabRecordModel(**labrecord_data)
        try:
            db.session.add(labrecord)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the lab record.")
        return labrecord, 201


@blp.route("/labrecord/<int:labrecord_id>")
class LabRecord(MethodView):
    @blp.response(200, LabRecordSchema)
    def get(self, labrecord_id):
        labrecord = db.session.get(LabRecordModel, labrecord_id)
        if labrecord is None:
            abort(404, message="Lab record not found")
        return labrecord

    @blp.arguments(LabRecordSchema)
    @blp.response(200, LabRecordSchema)
    def put(self, labrecord_data, labrecord_id):
        labrecord = db.session.get(LabRecordModel, labrecord_id)
        if labrecord is None:
            abort(404, message="Lab record not found")

        labrecord.patient_id = labrecord_data["patient_id"]
        labrecord.staff_id = labrecord_data["staff_id"]
        labrecord.test_type = labrecord_data["test_type"]
        labrecord.test_name = labrecord_data["test_name"]
        labrecord.test_date = labrecord_data["test_date"]
        labrecord.result = labrecord_data.get("result")
        labrecord.notes = labrecord_data.get("notes")

        try:
            db.session.add(labrecord)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the lab record.")
        return labrecord

    def delete(self, labrecord_id):
        labrecord = db.session.get(LabRecordModel, labrecord_id)
        if labrecord is None:
            abort(404, message="Lab record not found")

        try:
            db.session.delete(labrecord)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the lab record.")
        return {"message": "Lab record deleted."}, 200
