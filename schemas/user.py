from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    password = fields.Str(load_only=True)
