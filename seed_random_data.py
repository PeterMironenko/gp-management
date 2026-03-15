from __future__ import annotations

import argparse
import random
from datetime import date, datetime, timedelta

from werkzeug.security import generate_password_hash

from app import app, db, ensure_default_admin_user
from models import (
    DrugModel,
    LabRecordModel,
    MedicalInformationModel,
    MedicationModel,
    PatientModel,
    PositionModel,
    StaffModel,
    UserModel,
)


FIRST_NAMES = [
    "Liam",
    "Noah",
    "Oliver",
    "Elijah",
    "James",
    "Sophia",
    "Emma",
    "Charlotte",
    "Amelia",
    "Isabella",
    "Mia",
    "Evelyn",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Miller",
    "Davis",
    "Wilson",
    "Taylor",
    "Anderson",
    "Thomas",
    "Moore",
]

CITIES = ["London", "Manchester", "Birmingham", "Leeds", "Bristol"]
COUNTIES = ["Greater London", "Greater Manchester", "West Midlands", "West Yorkshire", "Bristol"]

DRUG_CATALOG = [
    ("Paracetamol", "Acetaminophen", "Tablet", "500mg", "MediCore"),
    ("Ibuprofen", "Ibuprofen", "Tablet", "400mg", "PharmaWell"),
    ("Amoxicillin", "Amoxicillin", "Capsule", "500mg", "BioHealth"),
    ("Metformin", "Metformin", "Tablet", "850mg", "GlucoLab"),
    ("Atorvastatin", "Atorvastatin", "Tablet", "20mg", "CardioRx"),
]

LAB_TEST_TYPES = ["Blood", "Urine", "Imaging", "Biochemistry"]
LAB_TEST_NAMES = ["CBC", "Lipid Panel", "HbA1c", "Liver Function", "Urinalysis", "X-Ray Chest"]
MED_ROUTES = ["Oral", "IV", "IM", "Topical"]


def random_dob(min_age: int = 18, max_age: int = 80) -> date:
    today = date.today()
    age = random.randint(min_age, max_age)
    days = random.randint(0, 364)
    return today - timedelta(days=(age * 365 + days))


def unique_phone(prefix: str, number: int, width: int = 8) -> str:
    return f"{prefix}{number:0{width}d}"


def maybe_reset_data(reset: bool) -> None:
    if not reset:
        return

    # Rebuild schema so model constraint changes (e.g. patient.staff_id non-unique)
    # are applied in SQLite without requiring a manual migration.
    db.drop_all()
    db.create_all()
    ensure_default_admin_user()


def ensure_positions_seeded() -> list[str]:
    allowed = ["doctor", "nurse", "physician", "paramedic"]
    existing = {row.position for row in PositionModel.query.all()}
    for position in allowed:
        if position not in existing:
            db.session.add(PositionModel(position=position))
    db.session.commit()
    return allowed


def create_related_medical_data(patient: PatientModel, staff: StaffModel, seed_index: int) -> None:
    now = datetime.now()

    drug_ids: list[int] = []
    for _ in range(random.randint(1, 3)):
        drug_name, generic_name, form, strength, manufacturer = random.choice(DRUG_CATALOG)
        drug = DrugModel(
            patient_id=patient.id,
            drug_name=drug_name,
            generic_name=generic_name,
            form=form,
            strength=strength,
            manufacturer=manufacturer,
            description=f"{drug_name} prescribed for patient care.",
        )
        db.session.add(drug)
        db.session.flush()
        drug_ids.append(drug.id)

    medical_information = MedicalInformationModel(
        patient_id=patient.id,
        primary_condition=random.choice(["Hypertension", "Diabetes", "Asthma", "Arthritis", None]),
        chronicillnesses=random.choice(["Hypertension", "Type 2 Diabetes", "None", "Asthma"]),
        allergies=random.choice(["Penicillin", "Pollen", "Latex", "None"]),
        surgeries=random.choice(["Appendectomy", "Tonsillectomy", "None"]),
        immunization=random.choice(["Flu 2025", "COVID-19 Booster", "Tetanus 2024"]),
        last_updated=now,
    )
    db.session.add(medical_information)

    for _ in range(random.randint(1, 3)):
        lab_record = LabRecordModel(
            patient_id=patient.id,
            staff_id=staff.id,
            test_type=random.choice(LAB_TEST_TYPES),
            test_name=random.choice(LAB_TEST_NAMES),
            test_date=now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23)),
            result=random.choice(["Normal", "Borderline", "Requires follow-up"]),
            notes=random.choice(["No concerns.", "Monitor over next 3 months.", "Repeat test recommended.", None]),
        )
        db.session.add(lab_record)

    for med_offset in range(random.randint(1, 2)):
        start = date.today() - timedelta(days=random.randint(0, 120))
        end = start + timedelta(days=random.randint(3, 90) + med_offset)
        medication = MedicationModel(
            patient_id=patient.id,
            drug_id=random.choice(drug_ids) if drug_ids else None,
            dosage=random.choice(["1 tablet", "2 tablets", "5 ml", "10 mg"]),
            frequency=random.choice(["Once daily", "Twice daily", "Every 8 hours", "As needed"]),
            route=random.choice(MED_ROUTES),
            start_date=start,
            end_date=end,
            notes=random.choice(["Take with food.", "Avoid alcohol.", "Short course.", None]),
        )
        db.session.add(medication)


def create_staff_and_patients(staff_count: int, patients_per_staff: int) -> None:
    positions = ensure_positions_seeded()

    base_user_index = (db.session.query(db.func.max(UserModel.id)).scalar() or 1) + 1
    base_patient_index = (db.session.query(db.func.max(PatientModel.id)).scalar() or 0) + 1

    patient_counter = base_patient_index

    for staff_offset in range(staff_count):
        user_index = base_user_index + staff_offset
        username = f"staff{user_index:03d}"
        password_hash = generate_password_hash("pass1234")

        user = UserModel(username=username, password=password_hash)
        db.session.add(user)
        db.session.flush()

        staff_first = random.choice(FIRST_NAMES)
        staff_last = random.choice(LAST_NAMES)
        staff = StaffModel(
            first_name=staff_first,
            last_name=staff_last,
            date_of_birth=random_dob(24, 65),
            work_phone=unique_phone("0207", user.id, 7),
            mobile_phone=unique_phone("07123", user.id, 6),
            work_email=f"{username}@clinic.local",
            position=random.choice(positions),
            user_id=user.id,
        )
        db.session.add(staff)
        db.session.flush()

        for _ in range(patients_per_staff):
            patient_first = random.choice(FIRST_NAMES)
            patient_last = random.choice(LAST_NAMES)
            now = datetime.now()

            patient = PatientModel(
                staff_id=staff.id,
                first_name=patient_first,
                last_name=patient_last,
                date_of_birth=random_dob(1, 95),
                landline_phone=unique_phone("0208", patient_counter, 7),
                mobile_phone=unique_phone("07999", patient_counter, 6),
                email=f"patient{patient_counter:05d}@example.com",
                address_street=f"{random.randint(1, 300)} High Street",
                address_city=random.choice(CITIES),
                address_county=random.choice(COUNTIES),
                address_postcode=f"AB{random.randint(10,99)} {random.randint(1,9)}CD",
                emergency_contact_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                emergency_contact_phone=unique_phone("07000", patient_counter, 6),
                created_at=now,
                updated_at=now,
            )
            db.session.add(patient)
            db.session.flush()
            create_related_medical_data(patient, staff, patient_counter)
            patient_counter += 1

    db.session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed random staff, patient and medical-domain data.")
    parser.add_argument("--staff", type=int, default=10, help="Number of staff to create (default: 10)")
    parser.add_argument(
        "--patients-per-staff",
        type=int,
        default=5,
        help="Number of patients per staff member (default: 5)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing seeded staff/patient/user data (keeps admin user id=1) before seeding",
    )
    args = parser.parse_args()

    with app.app_context():
        db.create_all()
        maybe_reset_data(args.reset)
        create_staff_and_patients(args.staff, args.patients_per_staff)

        staff_total = StaffModel.query.count()
        patient_total = PatientModel.query.count()
        drug_total = DrugModel.query.count()
        labrecord_total = LabRecordModel.query.count()
        medicalinformation_total = MedicalInformationModel.query.count()
        medication_total = MedicationModel.query.count()
        print(
            "Seeding complete: "
            f"staff={staff_total}, patients={patient_total}, "
            f"drugs={drug_total}, labrecords={labrecord_total}, "
            f"medicalinformation={medicalinformation_total}, medications={medication_total}"
        )


if __name__ == "__main__":
    main()
