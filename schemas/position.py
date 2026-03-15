from marshmallow import Schema, fields


class PositionSchema(Schema):
    id = fields.Int(dump_only=True)
    position = fields.Str(required=True)
