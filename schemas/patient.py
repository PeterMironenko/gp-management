from marshmallow import Schema, fields

class PatientSchema(Schema):
    id = fields.Int(dump_only=True)
    staff_id = fields.Int(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    date_of_birth = fields.Date(required=True)
    landline_phone = fields.Str(required=True)
    mobile_phone = fields.Str(required=True)
    email = fields.Str(required=True)
    address_street = fields.Str(required=True)
    address_city = fields.Str(required=True)
    address_county = fields.Str(required=True)
    address_postcode = fields.Str(required=True)
    emergency_contact_name = fields.Str(required=True)
    emergency_contact_phone = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

