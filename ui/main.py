import sys
from typing import List, Optional
import jwt

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from apiclient import ApiClient
from adminwindow import AdminWindow
from config import ConfigManager

class LoginDialog(QDialog):
    def __init__(self, api_client: ApiClient, config_manager: ConfigManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.api_client = api_client
        self.config_manager = config_manager
        self.setWindowTitle("Login")
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout()

        self.url_edit = QLineEdit(self.api_client.base_url)
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.open_register_dialog)

        layout.addWidget(QLabel("URL:"), 0, 0)
        layout.addWidget(self.url_edit, 0, 1)

        layout.addWidget(QLabel("Username:"), 1, 0)
        layout.addWidget(self.username_edit, 1, 1)
        layout.addWidget(QLabel("Password:"), 2, 0)
        layout.addWidget(self.password_edit, 2, 1)

        button_row = QHBoxLayout()
        button_row.addWidget(login_button)
        button_row.addWidget(register_button)
        layout.addLayout(button_row, 3, 0, 1, 2)

        self.setLayout(layout)

    def handle_login(self) -> None:
        url = self.url_edit.text().strip()
        self.api_client.base_url = url
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return
        try:
            self.api_client.login(username, password)
            # Save the API URL to config after successful login
            self.config_manager.set_api_url(url)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Login failed", str(exc))
            return
        self.accept()

    def open_register_dialog(self) -> None:
        dialog = RegisterDialog(self.api_client, self)
        if dialog.exec_() == QDialog.Accepted:
            # After successful registration, pre-fill username for convenience
            self.username_edit.setText(dialog.username())
            self.password_edit.setFocus()


class MainWindow(QMainWindow):
    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.api_client = api_client
        if self.api_client.is_admin:
            self.setWindowTitle("Store Manager (Admin)")
        else:
            self.setWindowTitle("Store Manager")
        self.resize(800, 600)

        self.stores: List[dict] = []
        self.items: List[dict] = []

        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        central = QWidget()
        main_layout = QHBoxLayout()

        # Left side: stores
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Stores"))
        self.store_list = QListWidget()
        self.store_list.currentItemChanged.connect(self.on_store_selected)
        left_layout.addWidget(self.store_list)

        store_btn_layout = QHBoxLayout()
        self.btn_refresh_stores = QPushButton("Refresh")
        self.btn_add_store = QPushButton("Add Store")
        self.btn_delete_store = QPushButton("Delete Store")
        if(not self.api_client.is_admin):
            self.btn_delete_store.setEnabled(False)
        self.btn_refresh_stores.clicked.connect(self.refresh_stores)
        self.btn_add_store.clicked.connect(self.add_store_dialog)
        self.btn_delete_store.clicked.connect(self.delete_selected_store)

        store_btn_layout.addWidget(self.btn_refresh_stores)
        store_btn_layout.addWidget(self.btn_add_store)
        store_btn_layout.addWidget(self.btn_delete_store)

        left_layout.addLayout(store_btn_layout)

        # Right side: items
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Items in selected store"))
        self.item_list = QListWidget()
        right_layout.addWidget(self.item_list)

        item_btn_layout = QHBoxLayout()
        self.btn_refresh_items = QPushButton("Refresh Items")
        self.btn_add_item = QPushButton("Add Item")
        self.btn_delete_item = QPushButton("Delete Item")
        if (not self.api_client.is_admin):
            self.btn_delete_item.setEnabled(False)
        self.btn_refresh_items.clicked.connect(self.refresh_items)
        self.btn_add_item.clicked.connect(self.add_item_dialog)
        self.btn_delete_item.clicked.connect(self.delete_selected_item)

        item_btn_layout.addWidget(self.btn_refresh_items)
        item_btn_layout.addWidget(self.btn_add_item)
        item_btn_layout.addWidget(self.btn_delete_item)

        right_layout.addLayout(item_btn_layout)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # --- Data loading helpers ---
    def refresh_data(self) -> None:
        self.refresh_stores()
        self.refresh_items()

    def refresh_stores(self) -> None:
        try:
            self.stores = self.api_client.list_stores()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.store_list.clear()
        for store in self.stores:
            item = QListWidgetItem(store.get("name", "<no name>"))
            item.setData(Qt.UserRole, store)
            self.store_list.addItem(item)

    def refresh_items(self) -> None:
        # Load all items from API and then filter by selected store
        try:
            all_items = self.api_client.list_items()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return

        selected_store = self.current_store()
        self.item_list.clear()
        self.items = []

        if not selected_store:
            return

        store_id = selected_store.get("id")
        for item in all_items:
            item_store = item.get("store") or {}
            if item_store.get("id") == store_id:
                self.items.append(item)
                list_item = QListWidgetItem(f"{item.get('name')} - ${item.get('price')}")
                list_item.setData(Qt.UserRole, item)
                self.item_list.addItem(list_item)

    def current_store(self) -> Optional[dict]:
        current = self.store_list.currentItem()
        if not current:
            return None
        return current.data(Qt.UserRole)

    def current_item(self) -> Optional[dict]:
        current = self.item_list.currentItem()
        if not current:
            return None
        return current.data(Qt.UserRole)

    # --- Store actions ---
    def add_store_dialog(self) -> None:
        name, ok = QInputDialogWithText.get_text(self, "Add Store", "Store name:")
        if not ok or not name:
            return
        try:
            self.api_client.add_store(name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.refresh_stores()

    def delete_selected_store(self) -> None:
        store = self.current_store()
        if not store:
            QMessageBox.information(self, "Delete Store", "Please select a store first.")
            return
        name = store.get("name")
        if QMessageBox.question(self, "Confirm", f"Delete store '{name}'?") != QMessageBox.Yes:
            return
        try:
            self.api_client.delete_store(name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.refresh_stores()
        self.item_list.clear()

    # --- Item actions ---
    def add_item_dialog(self) -> None:
        store = self.current_store()
        if not store:
            QMessageBox.information(self, "Add Item", "Please select a store first.")
            return
        dialog = AddItemDialog(store, self)
        if dialog.exec_() == QDialog.Accepted:
            name, price = dialog.get_values()
            try:
                self.api_client.add_item(name=name, price=price, store_id=store.get("id"))
            except Exception as exc:  # noqa: BLE001
                QMessageBox.critical(self, "Error", str(exc))
                return
            self.refresh_items()

    def delete_selected_item(self) -> None:
        item = self.current_item()
        if not item:
            QMessageBox.information(self, "Delete Item", "Please select an item first.")
            return
        name = item.get("name")
        if QMessageBox.question(self, "Confirm", f"Delete item '{name}'?") != QMessageBox.Yes:
            return
        try:
            self.api_client.delete_item(name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return
        self.refresh_items()

    def on_store_selected(self, _current: QListWidgetItem, _previous: QListWidgetItem | None) -> None:  # noqa: D401, ARG002
        # Whenever store selection changes, refresh items list
        self.refresh_items()


class QInputDialogWithText(QDialog):
    """Simple reusable dialog for getting a single line of text."""

    def __init__(self, parent: QWidget | None, title: str, label: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self._value: str = ""

        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))

        self._edit = QLineEdit()
        layout.addWidget(self._edit)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    @classmethod
    def get_text(cls, parent: QWidget | None, title: str, label: str) -> tuple[str, bool]:
        dialog = cls(parent, title, label)
        result = dialog.exec_()
        return dialog._edit.text().strip(), result == QDialog.Accepted


class RegisterDialog(QDialog):
    """Dialog used to register a new user via the API."""

    def __init__(self, api_client: ApiClient, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.api_client = api_client
        self._username: str = ""
        self.setWindowTitle("Register User")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_confirm_edit = QLineEdit()
        self.password_confirm_edit.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Username:"), 0, 0)
        layout.addWidget(self.username_edit, 0, 1)
        layout.addWidget(QLabel("Password:"), 1, 0)
        layout.addWidget(self.password_edit, 1, 1)
        layout.addWidget(QLabel("Confirm Password:"), 2, 0)
        layout.addWidget(self.password_confirm_edit, 2, 1)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Register")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.on_register_clicked)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def on_register_clicked(self) -> None:
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        password_confirm = self.password_confirm_edit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        try:
            self.api_client.register(username, password)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Registration failed", str(exc))
            return

        self._username = username
        QMessageBox.information(self, "Success", "User registered successfully.")
        self.accept()

    def username(self) -> str:
        return self._username


class AddItemDialog(QDialog):
    def __init__(self, store: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.setWindowTitle(f"Add Item to {store.get('name')}")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout()

        self.name_edit = QLineEdit()
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.0, 1_000_000.0)
        self.price_spin.setDecimals(2)

        layout.addWidget(QLabel("Name:"), 0, 0)
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel("Price:"), 1, 0)
        layout.addWidget(self.price_spin, 1, 1)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_values(self) -> tuple[str, float]:
        name = self.name_edit.text().strip()
        price = float(self.price_spin.value())
        return name, price


def main() -> None:
    app = QApplication(sys.argv)

    # Load configuration
    config_manager = ConfigManager()
    api_url = config_manager.get_api_url()

    api_client = ApiClient(api_url)

    login_dialog = LoginDialog(api_client, config_manager)
    if login_dialog.exec_() != QDialog.Accepted:
        sys.exit(0)

    if api_client.is_admin:
        window = AdminWindow(api_client)
    else:
        window = MainWindow(api_client)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
