from app import app, ensure_default_positions
from models import PositionModel


def test_positions_api_returns_allowed_values_for_admin(client):
    client.post("/register", json={"username": "admin", "password": "secret"})
    login_resp = client.post("/login", json={"username": "admin", "password": "secret"})
    access_token = login_resp.get_json()["access_token"]

    with app.app_context():
        ensure_default_positions()

    resp = client.get("/position", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    data = resp.get_json()
    values = {row["position"] for row in data}
    assert values == {"doctor", "nurse", "physician", "paramedic"}


def test_positions_table_contains_allowed_values(client):
    with app.app_context():
        ensure_default_positions()
        rows = PositionModel.query.order_by(PositionModel.id.asc()).all()
        values = {row.position for row in rows}

    assert values == {"doctor", "nurse", "physician", "paramedic"}
