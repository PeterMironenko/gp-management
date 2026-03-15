from marshmallow import Schema, fields


class DrugSchema(Schema):
    id = fields.Int(dump_only=True)
    drug_name = fields.Str(required=True)
    generic_name = fields.Str(load_default=None)
    form = fields.Str(load_default=None)
    strength = fields.Str(load_default=None)
    manufacturer = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    is_approval_required = fields.Bool(load_default=True)
