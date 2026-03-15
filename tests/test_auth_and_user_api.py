from __future__ import annotations

from typing import Tuple

from app import app
from models import StaffModel, UserModel


def register_user(client, username: str = "user1", password: str = "abcxyz") -> None:
    resp = client.post("/register", json={"username": username, "password": password})
    assert resp.status_code == 201


def login_user(client, username: str = "user1", password: str = "abcxyz") -> Tuple[str, str]:
    resp = client.post("/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data["access_token"], data["refresh_token"]


def auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def get_user_id_by_username(username: str) -> int:
    with app.app_context():
        user = UserModel.find_by_username(username)
        assert user is not None
        return user.id


def get_staff_by_user_id(user_id: int):
    with app.app_context():
        return StaffModel.query.filter_by(user_id=user_id).first()


def test_register_and_login_returns_tokens(client):
    register_user(client)
    access_token, refresh_token = login_user(client)

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    assert access_token
    assert refresh_token

    user_id = get_user_id_by_username("user1")
    staff = get_staff_by_user_id(user_id)
    assert staff is not None
    assert staff.user_id == user_id
    assert staff.first_name == "user1"
    assert staff.work_email == f"user1.{user_id}@staff.local"


def test_register_duplicate_user_conflict(client):
    register_user(client, username="dup_user", password="secret")

    resp = client.post("/register", json={"username": "dup_user", "password": "secret"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "already exists" in data["message"]


def test_login_invalid_credentials(client):
    register_user(client, username="badlogin", password="secret")

    resp = client.post("/login", json={"username": "badlogin", "password": "wrong"})
    assert resp.status_code == 401


def test_logout_requires_and_revokes_token(client):
    register_user(client)
    access_token, _ = login_user(client)

    no_token_resp = client.post("/logout")
    assert no_token_resp.status_code == 401
    no_token_data = no_token_resp.get_json()
    assert no_token_data["error"] == "authorization_required"

    headers = auth_header(access_token)
    logout_resp = client.post("/logout", headers=headers)
    assert logout_resp.status_code == 200

    second_logout_resp = client.post("/logout", headers=headers)
    assert second_logout_resp.status_code == 401
    second_logout_data = second_logout_resp.get_json()
    assert second_logout_data["error"] == "token_revoked"


def test_user_list_and_get_by_id(client):
    register_user(client, username="u1", password="secret")
    register_user(client, username="u2", password="secret")
    admin_access_token, _ = login_user(client, username="u1", password="secret")

    list_resp = client.get("/user", headers=auth_header(admin_access_token))
    assert list_resp.status_code == 200
    users = list_resp.get_json()
    assert isinstance(users, list)
    assert len(users) == 2

    target_user = next(user for user in users if user["username"] == "u1")
    user_id = target_user["id"]

    get_resp = client.get(f"/user/{user_id}", headers=auth_header(admin_access_token))
    assert get_resp.status_code == 200
    user_data = get_resp.get_json()
    assert user_data["id"] == user_id
    assert user_data["username"] == "u1"


def test_user_get_not_found(client):
    register_user(client, username="admin", password="secret")
    admin_access_token, _ = login_user(client, username="admin", password="secret")

    resp = client.get("/user/99999", headers=auth_header(admin_access_token))
    assert resp.status_code == 404


def test_user_delete_by_id(client):
    register_user(client, username="admin", password="secret")
    register_user(client, username="delete_me", password="secret")
    admin_access_token, _ = login_user(client, username="admin", password="secret")

    list_resp = client.get("/user", headers=auth_header(admin_access_token))
    users = list_resp.get_json()
    user_id = next(user["id"] for user in users if user["username"] == "delete_me")

    delete_resp = client.delete(f"/user/{user_id}", headers=auth_header(admin_access_token))
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/user/{user_id}", headers=auth_header(admin_access_token))
    assert get_resp.status_code == 404

    deleted_user_staff = get_staff_by_user_id(user_id)
    assert deleted_user_staff is None


def test_user_update_syncs_staff_table(client):
    register_user(client, username="admin", password="secret")
    register_user(client, username="member", password="secret")
    admin_access_token, _ = login_user(client, username="admin", password="secret")

    member_id = get_user_id_by_username("member")

    update_resp = client.put(
        f"/user/{member_id}",
        headers=auth_header(admin_access_token),
        json={"username": "member_updated", "password": "newsecret"},
    )
    assert update_resp.status_code == 200
    updated_user = update_resp.get_json()
    assert updated_user["id"] == member_id
    assert updated_user["username"] == "member_updated"

    staff = get_staff_by_user_id(member_id)
    assert staff is not None
    assert staff.first_name == "member_updated"
    assert staff.work_email == f"member_updated.{member_id}@staff.local"


def test_non_admin_user_cannot_access_protected_user_api(client):
    register_user(client, username="admin", password="secret")
    register_user(client, username="member", password="secret")

    member_access_token, member_refresh_token = login_user(client, username="member", password="secret")

    list_resp = client.get("/user", headers=auth_header(member_access_token))
    assert list_resp.status_code == 403

    logout_resp = client.post("/logout", headers=auth_header(member_access_token))
    assert logout_resp.status_code == 403

    refresh_resp = client.post("/refresh", headers=auth_header(member_refresh_token))
    assert refresh_resp.status_code == 403
