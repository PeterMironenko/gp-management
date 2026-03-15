from marshmallow import Schema, fields


class AppointmentSchema(Schema):
    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    staff_id = fields.Int(required=True)
    appointment_date = fields.DateTime(required=True)
    duration_minutes = fields.Int(required=True)
    reason = fields.Str(required=True)
    notes = fields.Str(load_default=None)
    location = fields.Str(load_default=None)
