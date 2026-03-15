from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import DrugModel, db
from schemas import DrugSchema


blp = Blueprint("Drugs", __name__, description="Operations on drugs")


@blp.route("/drug")
class DrugList(MethodView):
    @blp.response(200, DrugSchema(many=True))
    def get(self):
        return DrugModel.query.order_by(DrugModel.id.asc()).all()

    @blp.arguments(DrugSchema)
    @blp.response(201, DrugSchema)
    def post(self, drug_data):
        drug = DrugModel(**drug_data)
        try:
            db.session.add(drug)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the drug.")
        return drug, 201


@blp.route("/drug/<int:drug_id>")
class Drug(MethodView):
    @blp.response(200, DrugSchema)
    def get(self, drug_id):
        drug = db.session.get(DrugModel, drug_id)
        if drug is None:
            abort(404, message="Drug not found")
        return drug

    @blp.arguments(DrugSchema)
    @blp.response(200, DrugSchema)
    def put(self, drug_data, drug_id):
        drug = db.session.get(DrugModel, drug_id)
        if drug is None:
            abort(404, message="Drug not found")

        drug.drug_name = drug_data["drug_name"]
        drug.generic_name = drug_data.get("generic_name")
        drug.form = drug_data.get("form")
        drug.strength = drug_data.get("strength")
        drug.manufacturer = drug_data.get("manufacturer")
        drug.description = drug_data.get("description")
        drug.is_approval_required = drug_data.get("is_approval_required", drug.is_approval_required)

        try:
            db.session.add(drug)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while updating the drug.")
        return drug

    def delete(self, drug_id):
        drug = db.session.get(DrugModel, drug_id)
        if drug is None:
            abort(404, message="Drug not found")

        try:
            db.session.delete(drug)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while deleting the drug.")
        return {"message": "Drug deleted."}, 200
