from datetime import date, datetime

from app import app, db
from models import PatientModel, StaffModel, UserModel


def _seed_staff(username: str = "staff_api") -> StaffModel:
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


def _seed_patient(email: str = "patient.api@example.com") -> tuple[int, int]:
    now = datetime.now()
    staff = _seed_staff(username=f"staff_{email.split('@')[0]}")
    patient = PatientModel(
        staff_id=staff.id,
        first_name="Pat",
        last_name="Ient",
        date_of_birth=date(1990, 1, 1),
        landline_phone=f"0207000{staff.id:04d}",
        mobile_phone=f"0712300{staff.id:04d}",
        email=email,
        address_street="1 Test Street",
        address_city="London",
        address_county="Greater London",
        address_postcode="SW1A 1AA",
        emergency_contact_name="Emergency Contact",
        emergency_contact_phone=f"0700000{staff.id:04d}",
        created_at=now,
        updated_at=now,
    )
    db.session.add(patient)
    db.session.commit()
    return patient.id, patient.staff_id


def test_drug_crud_endpoints(client):
    with app.app_context():
        patient_id, _ = _seed_patient(email="drug.patient@example.com")

    create_payload = {
        "patient_id": patient_id,
        "drug_name": "Amoxicillin",
        "generic_name": "Amoxicillin",
        "form": "Capsule",
        "strength": "500mg",
        "manufacturer": "ACME Pharma",
        "description": "Antibiotic",
    }
    create_resp = client.post("/drug", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.get_json()
    drug_id = created["id"]

    get_resp = client.get(f"/drug/{drug_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["drug_name"] == "Amoxicillin"

    list_resp = client.get(f"/drug?patient_id={patient_id}")
    assert list_resp.status_code == 200
    listed = list_resp.get_json()
    assert len(listed) == 1
    assert listed[0]["id"] == drug_id

    update_payload = {
        **create_payload,
        "drug_name": "Amoxicillin Updated",
        "description": "Updated description",
    }
    update_resp = client.put(f"/drug/{drug_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.get_json()["drug_name"] == "Amoxicillin Updated"

    delete_resp = client.delete(f"/drug/{drug_id}")
    assert delete_resp.status_code == 200

    not_found = client.get(f"/drug/{drug_id}")
    assert not_found.status_code == 404


def test_labrecord_crud_endpoints(client):
    with app.app_context():
        patient_id, staff_id = _seed_patient(email="lab.patient@example.com")

    create_payload = {
        "patient_id": patient_id,
        "staff_id": staff_id,
        "test_type": "Blood",
        "test_name": "CBC",
        "test_date": "2026-02-21T09:00:00",
        "result": "Normal",
        "notes": "No abnormalities",
    }
    create_resp = client.post("/labrecord", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.get_json()
    labrecord_id = created["id"]

    get_resp = client.get(f"/labrecord/{labrecord_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["test_name"] == "CBC"

    list_resp = client.get(f"/labrecord?patient_id={patient_id}")
    assert list_resp.status_code == 200
    listed = list_resp.get_json()
    assert len(listed) == 1
    assert listed[0]["id"] == labrecord_id

    update_payload = {
        **create_payload,
        "test_name": "CBC Updated",
        "result": "Borderline",
    }
    update_resp = client.put(f"/labrecord/{labrecord_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.get_json()["test_name"] == "CBC Updated"

    delete_resp = client.delete(f"/labrecord/{labrecord_id}")
    assert delete_resp.status_code == 200

    not_found = client.get(f"/labrecord/{labrecord_id}")
    assert not_found.status_code == 404


def test_medicalinformation_crud_endpoints(client):
    with app.app_context():
        patient_id, _ = _seed_patient(email="medicalinfo.patient@example.com")

    create_payload = {
        "patient_id": patient_id,
        "primary_condition": "Hypertension",
        "chronicillnesses": "Hypertension",
        "allergies": "Penicillin",
        "surgeries": "Appendectomy",
        "immunization": "Flu 2025",
        "last_updated": "2026-02-21T10:30:00",
    }
    create_resp = client.post("/medicalinformation", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.get_json()
    medicalinformation_id = created["id"]

    get_resp = client.get(f"/medicalinformation/{medicalinformation_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["primary_condition"] == "Hypertension"

    list_resp = client.get(f"/medicalinformation?patient_id={patient_id}")
    assert list_resp.status_code == 200
    listed = list_resp.get_json()
    assert len(listed) == 1
    assert listed[0]["id"] == medicalinformation_id

    update_payload = {
        **create_payload,
        "allergies": "Penicillin, Latex",
    }
    update_resp = client.put(f"/medicalinformation/{medicalinformation_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert "Latex" in update_resp.get_json()["allergies"]

    delete_resp = client.delete(f"/medicalinformation/{medicalinformation_id}")
    assert delete_resp.status_code == 200

    not_found = client.get(f"/medicalinformation/{medicalinformation_id}")
    assert not_found.status_code == 404


def test_medication_crud_endpoints(client):
    with app.app_context():
        patient_id, _ = _seed_patient(email="medication.patient@example.com")

    create_payload = {
        "patient_id": patient_id,
        "drug_id": None,
        "dosage": "1 tablet",
        "frequency": "Twice daily",
        "route": "Oral",
        "start_date": "2026-02-20",
        "end_date": "2026-03-01",
        "notes": "After meals",
    }
    create_resp = client.post("/medication", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.get_json()
    medication_id = created["id"]

    get_resp = client.get(f"/medication/{medication_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["dosage"] == "1 tablet"

    list_resp = client.get(f"/medication?patient_id={patient_id}")
    assert list_resp.status_code == 200
    listed = list_resp.get_json()
    assert len(listed) == 1
    assert listed[0]["id"] == medication_id

    update_payload = {
        **create_payload,
        "dosage": "2 tablets",
        "frequency": "Once daily",
    }
    update_resp = client.put(f"/medication/{medication_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.get_json()["dosage"] == "2 tablets"

    delete_resp = client.delete(f"/medication/{medication_id}")
    assert delete_resp.status_code == 200

    not_found = client.get(f"/medication/{medication_id}")
    assert not_found.status_code == 404
