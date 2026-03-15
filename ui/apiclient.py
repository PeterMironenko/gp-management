import requests
import jwt
from typing import List

class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token: str = ""
        self.is_admin: bool = False

    def _headers(self, needs_auth: bool = False) -> dict:
        headers = {"Content-Type": "application/json"}
        if needs_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    # --- Auth ---
    def register(self, username: str, password: str) -> None:
        url = f"{self.base_url}/register"
        resp = requests.post(
            url,
            json={"username": username, "password": password},
            headers=self._headers(),
        )
        if resp.status_code not in (200, 201):
            message = None
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                message = resp.json().get("message")
            raise RuntimeError(message or f"Registration failed: {resp.status_code}")

    def login(self, username: str, password: str) -> None:
        url = f"{self.base_url}/login"
        print("headers:", self._headers())
        resp = requests.post(url, json={"username": username, "password": password}, headers=self._headers())
        if resp.status_code != 200:
            raise RuntimeError(resp.json().get("message", f"Login failed: {resp.status_code}"))
        data = resp.json()
        self.access_token = data.get("access_token")
        payload = jwt.decode(self.access_token, options={"verify_signature": False})
        self.is_admin = payload.get("is_admin", False)

        print("Access token received:", self.access_token)
        if  len(self.access_token) == 0:
            raise RuntimeError("No access token received from server.")

    # --- Stores ---
    def list_stores(self) -> List[dict]:
        url = f"{self.base_url}/store"
        print("self.access_token:", self.access_token)
        print("self._headers(needs_auth=True):", self._headers(needs_auth=True))
        resp = requests.get(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to load stores: {resp.status_code}")
        return resp.json()

    def add_store(self, name: str) -> dict:
        url = f"{self.base_url}/store/{name}"
        resp = requests.post(url, headers=self._headers(needs_auth=True))
        if resp.status_code not in (200, 201):
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to add store: {resp.status_code}")
        return resp.json()

    def delete_store(self, name: str) -> None:
        url = f"{self.base_url}/store/{name}"
        resp = requests.delete(url, headers=self._headers())
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to delete store: {resp.status_code}")

    # --- Items ---
    def list_items(self) -> List[dict]:
        url = f"{self.base_url}/item"
        print("list_items: self._headers(needs_auth=True):", self._headers(needs_auth=True))
        resp = requests.get(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to load items: {resp.status_code}")
        return resp.json()

    def add_item(self, name: str, price: float, store_id: int) -> dict:
        url = f"{self.base_url}/item/{name}"
        payload = {"price": price, "store_id": store_id}
        resp = requests.post(url, json=payload, headers=self._headers(needs_auth=True))
        if resp.status_code not in (200, 201):
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to add item: {resp.status_code}")
        return resp.json()

    def delete_item(self, name: str) -> None:
        url = f"{self.base_url}/item/{name}"
        resp = requests.delete(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to delete item: {resp.status_code}")
        
    # --- User management ---
    def list_users(self) -> List[dict]:
        url = f"{self.base_url}/user"
        resp = requests.get(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to load users: {resp.status_code}")
        return resp.json()

    def get_user(self, user_id: int) -> dict:
        url = f"{self.base_url}/user/{user_id}"
        resp = requests.get(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to get user: {resp.status_code}")
        return resp.json()

    def delete_user(self, user_id: int) -> None:
        url = f"{self.base_url}/user/{user_id}"
        resp = requests.delete(url, headers=self._headers(needs_auth=True))
        if resp.status_code != 200:
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to delete user: {resp.status_code}")
    
    def create_user(self, username: str, password: str) -> dict:
        url = f"{self.base_url}/register"
        resp = requests.post(url, json={"username": username, "password": password}, headers=self._headers())
        if resp.status_code not in (200, 201):
            message = resp.json().get("message") if resp.headers.get("Content-Type", "").startswith("application/json") else None
            raise RuntimeError(message or f"Failed to create user: {resp.status_code}")
        return resp.json()

