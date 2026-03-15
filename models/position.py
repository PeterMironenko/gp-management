from models import db


class PositionModel(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(30), unique=True, nullable=False)
