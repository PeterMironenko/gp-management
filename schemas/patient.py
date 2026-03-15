from marshmallow import Schema, fields

class PlainPatientSchema(Schema):
    id = fields.Int(dump_only=True)
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
    username = fields.Str(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)


class PatientSchema(PlainPatientSchema):
    store_id = fields.Int(required=True, load_only=True)
    # Use lazy string reference to avoid circular import with store_schemas
    store = fields.Nested("PlainStoreSchema", dump_only=True)

class PatientUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
