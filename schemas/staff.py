from marshmallow import Schema, fields


class StaffSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    date_of_birth = fields.Date(required=True)
    work_phone = fields.Str(required=True)
    mobile_phone = fields.Str(required=True)
    work_email = fields.Str(required=True)
    position = fields.Str(required=True)
    user_id = fields.Int(dump_only=True)
