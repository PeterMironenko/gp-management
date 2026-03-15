import os
import sys

import pytest

# Ensure project root is on sys.path so `app` and `db` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    # if you need app context in tests, you can also:
    # with app.app_context():
    #     yield app
    return app

@pytest.fixture(scope="session")
def db(app):
    # app context is required to use SQLAlchemy
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app, db):
    """Ensure each test runs with an empty database while sharing app/db objects."""
    with app.app_context():
        # Delete from all tables in reverse dependency order
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()