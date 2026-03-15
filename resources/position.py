from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt, jwt_required

from models import PositionModel
from schemas import PositionSchema


blp = Blueprint("Positions", "positions", description="Operations on positions")


def _ensure_admin():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        abort(403, message="Admin privilege required.")


@blp.route("/position")
class PositionList(MethodView):
    @jwt_required()
    @blp.response(200, PositionSchema(many=True))
    def get(self):
        _ensure_admin()
        return PositionModel.query.order_by(PositionModel.position.asc()).all()
