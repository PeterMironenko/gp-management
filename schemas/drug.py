from marshmallow import Schema, fields


class DrugSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    drug_name = fields.Str(required=True)
    generic_name = fields.Str(load_default=None)
    form = fields.Str(load_default=None)
    strength = fields.Str(load_default=None)
    manufacturer = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
