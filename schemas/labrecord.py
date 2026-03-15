from marshmallow import Schema, fields


class LabRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    staff_id = fields.Int(required=True)
    test_type = fields.Str(required=True)
    test_name = fields.Str(required=True)
    test_date = fields.DateTime(required=True)
    result = fields.Str(load_default=None)
    notes = fields.Str(load_default=None)
