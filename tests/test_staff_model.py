from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import app, db
from models import StaffModel, UserModel


def test_staff_has_one_to_one_relationship_with_user(client):
    with app.app_context():
        user = UserModel(username="staff_user", password="secret")
        db.session.add(user)
        db.session.commit()

        staff = StaffModel(
            first_name="Anna",
            last_name="Smith",
            date_of_birth=date(1985, 6, 15),
            work_phone="02070000011",
            mobile_phone="07123450011",
            work_email="anna.smith@clinic.local",
            position="GP",
            user_id=user.id,
        )
        db.session.add(staff)
        db.session.commit()

        saved_staff = StaffModel.query.filter_by(user_id=user.id).first()
        saved_user = UserModel.find_by_id(user.id)

        assert saved_staff is not None
        assert saved_user is not None
        assert saved_staff.user.id == user.id
        assert saved_user.staff.id == saved_staff.id


def test_staff_user_relationship_is_unique_per_user(client):
    with app.app_context():
        user = UserModel(username="unique_staff_user", password="secret")
        db.session.add(user)
        db.session.commit()

        first_staff = StaffModel(
            first_name="John",
            last_name="Brown",
            date_of_birth=date(1980, 1, 1),
            work_phone="02070000021",
            mobile_phone="07123450021",
            work_email="john.brown@clinic.local",
            position="Nurse",
            user_id=user.id,
        )
        db.session.add(first_staff)
        db.session.commit()

        second_staff = StaffModel(
            first_name="Mark",
            last_name="Taylor",
            date_of_birth=date(1982, 2, 2),
            work_phone="02070000022",
            mobile_phone="07123450022",
            work_email="mark.taylor@clinic.local",
            position="Therapist",
            user_id=user.id,
        )
        db.session.add(second_staff)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
