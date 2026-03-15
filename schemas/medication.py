from marshmallow import Schema, fields


class MedicationSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    drug_id = fields.Int(load_default=None)
    dosage = fields.Str(required=True)
    frequency = fields.Str(required=True)
    route = fields.Str(load_default=None)
    start_date = fields.Date(required=True)
    end_date = fields.Date(load_default=None)
    notes = fields.Str(load_default=None)
