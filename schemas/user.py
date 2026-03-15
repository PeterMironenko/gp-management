from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    staff = fields.Nested("StaffSchema", dump_only=True)


class UserCreateSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    first_name = fields.Str(load_default=None)
    last_name = fields.Str(load_default=None)
    date_of_birth = fields.Date(load_default=None)
    work_phone = fields.Str(load_default=None)
    mobile_phone = fields.Str(load_default=None)
    work_email = fields.Str(load_default=None)
    position = fields.Str(load_default=None)


class UserUpdateSchema(Schema):
    username = fields.Str(load_default=None)
    password = fields.Str(load_default=None, load_only=True)
    first_name = fields.Str(load_default=None)
    last_name = fields.Str(load_default=None)
    date_of_birth = fields.Date(load_default=None)
    work_phone = fields.Str(load_default=None)
    mobile_phone = fields.Str(load_default=None)
    work_email = fields.Str(load_default=None)
    position = fields.Str(load_default=None)
