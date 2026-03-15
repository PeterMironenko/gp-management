from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import db, StoreModel
from schemas import StoreSchema


blp = Blueprint("Stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            store_pk = int(store_id)
        except ValueError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found")

        store = db.session.get(StoreModel, store_pk)
        if store is None:
            abort(HTTPStatus.NOT_FOUND, message="Store not found")

        return store

    def delete(self, store_id):
        try:
            store_pk = int(store_id)
        except ValueError:
            abort(HTTPStatus.NOT_FOUND, message="Store not found")

        store = db.session.get(StoreModel, store_pk)
        if store is None:
            abort(HTTPStatus.NOT_FOUND, message="Store not found")

        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}, HTTPStatus.OK


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(HTTPStatus.CREATED, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                HTTPStatus.BAD_REQUEST,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred creating the store.")

        return store
