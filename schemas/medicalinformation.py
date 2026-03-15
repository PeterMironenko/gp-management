from marshmallow import Schema, fields


class MedicalInformationSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    primary_condition = fields.Str(load_default=None)
    chronicillnesses = fields.Str(load_default=None)
    allergies = fields.Str(load_default=None)
    surgeries = fields.Str(load_default=None)
    immunization = fields.Str(load_default=None)
    last_updated = fields.DateTime(required=True)
