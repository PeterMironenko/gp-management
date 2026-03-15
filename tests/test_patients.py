from datetime import date, datetime

from app import app, db
from models import PatientModel, StaffModel, UserModel


def _seed_staff(username: str = "staff_user") -> StaffModel:
    user = UserModel(username=username, password="secret")
    db.session.add(user)
    db.session.flush()

    staff = StaffModel(
        first_name="Staff",
        last_name="Member",
        date_of_birth=date(1980, 1, 1),
        work_phone=f"0207{user.id:07d}",
        mobile_phone=f"07123{user.id:06d}",
        work_email=f"{username}@clinic.local",
        position="doctor",
        user_id=user.id,
    )
    db.session.add(staff)
    db.session.flush()
    return staff


def test_patients_table_insert_and_query(client):
    now = datetime.now()

    with app.app_context():
        staff = _seed_staff(username="staff_for_patient_insert")
        patient = PatientModel(
            staff_id=staff.id,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            landline_phone="02070000001",
            mobile_phone="07123456789",
            email="john.doe@example.com",
            address_street="1 Test Street",
            address_city="London",
            address_county="Greater London",
            address_postcode="SW1A 1AA",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="07123450000",
            created_at=now,
            updated_at=now,
        )

        db.session.add(patient)
        db.session.commit()

        saved_patient = PatientModel.query.filter_by(email="john.doe@example.com").first()

        assert saved_patient is not None
        assert saved_patient.first_name == "John"
        assert saved_patient.last_name == "Doe"
        assert saved_patient.id is not None


def _seed_patient(email: str = "john.doe@example.com") -> PatientModel:
    now = datetime.now()
    staff = _seed_staff(username=f"staff_{email.split('@')[0]}")
    patient = PatientModel(
        staff_id=staff.id,
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 1),
        landline_phone="02070000001",
        mobile_phone="07123456789",
        email=email,
        address_street="1 Test Street",
        address_city="London",
        address_county="Greater London",
        address_postcode="SW1A 1AA",
        emergency_contact_name="Jane Doe",
        emergency_contact_phone="07123450000",
        created_at=now,
        updated_at=now,
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def test_get_patient_by_id_returns_patient(client):
    with app.app_context():
        patient = _seed_patient(email="john.get@example.com")
        patient_id = patient.id

    resp = client.get(f"/patient/{patient_id}")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == patient_id
    assert data["email"] == "john.get@example.com"


def test_get_patient_by_id_not_found(client):
    resp = client.get("/patient/99999")

    assert resp.status_code == 404


def test_put_patient_by_id_updates_existing_patient(client):
    with app.app_context():
        patient = _seed_patient(email="john.put.before@example.com")
        patient_id = patient.id

    payload = {
        "staff_id": patient.staff_id,
        "first_name": "Johnny",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "landline_phone": "02070000002",
        "mobile_phone": "07123456788",
        "email": "john.put.after@example.com",
        "address_street": "2 Updated Street",
        "address_city": "London",
        "address_county": "Greater London",
        "address_postcode": "SW1A 1AB",
        "emergency_contact_name": "Janet Doe",
        "emergency_contact_phone": "07123450001",
    }
    resp = client.put(f"/patient/{patient_id}", json=payload)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == patient_id
    assert data["first_name"] == "Johnny"
    assert data["email"] == "john.put.after@example.com"


def test_delete_patient_by_id_removes_patient(client):
    with app.app_context():
        patient = _seed_patient(email="john.delete@example.com")
        patient_id = patient.id

    delete_resp = client.delete(f"/patient/{patient_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/patient/{patient_id}")
    assert get_resp.status_code == 404
