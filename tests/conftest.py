import pytest

from app import app, db
from blocklist import BLOCKLIST


@pytest.fixture()
def client():
    """Return a Flask test client with a fresh database per test."""
    app.config["TESTING"] = True

    with app.app_context():
        # Fresh DB for each test
        db.drop_all()
        db.create_all()
        # Clear any revoked tokens
        BLOCKLIST.clear()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
