from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import db, ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema)
    def get(self, item_id):
        try:
            item_pk = int(item_id)
        except ValueError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found")

        item = db.session.get(ItemModel, item_pk)
        if item is None:
            abort(HTTPStatus.NOT_FOUND, message="Item not found")

        return item

    def delete(self, item_id):
        try:
            item_pk = int(item_id)
        except ValueError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found")

        item = db.session.get(ItemModel, item_pk)
        if item is None:
            abort(HTTPStatus.NOT_FOUND, message="Item not found")

        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}, HTTPStatus.OK

    @blp.arguments(ItemUpdateSchema)
    @blp.response(HTTPStatus.OK, ItemSchema)
    def put(self, item_data, item_id):
        try:
            item_pk = int(item_id)
        except ValueError:
            abort(HTTPStatus.NOT_FOUND, message="Item not found")

        item = db.session.get(ItemModel, item_pk)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_pk, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(HTTPStatus.OK, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(HTTPStatus.CREATED, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message="An error occurred while inserting the item.")

        return item
