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

class AdminWindow(QMainWindow):
    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.api_client = api_client
        self.setWindowTitle("Admin Panel - User Management")
        self.resize(700, 600)
        self.users: List[dict] = []
        
        self._build_ui()
        self.refresh_users()
    
    def _build_ui(self) -> None:
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("User Management")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Users list section
        list_label = QLabel("Existing Users:")
        main_layout.addWidget(list_label)
        
        self.users_list = QListWidget()
        self.users_list.itemSelectionChanged.connect(self.on_user_selected)
        main_layout.addWidget(self.users_list)
        
        # User action buttons
        user_actions_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_users)
        user_actions_layout.addWidget(refresh_button)
        
        delete_button = QPushButton("Delete Selected User")
        delete_button.clicked.connect(self.delete_selected_user)
        user_actions_layout.addWidget(delete_button)
        
        main_layout.addLayout(user_actions_layout)
        
        # New user registration section
        register_label = QLabel("Register New User:")
        register_font = register_label.font()
        register_font.setPointSize(11)
        register_font.setBold(True)
        register_label.setFont(register_font)
        main_layout.addWidget(register_label)
        
        register_form_layout = QGridLayout()
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Username")
        register_form_layout.addWidget(QLabel("Username:"), 0, 0)
        register_form_layout.addWidget(self.register_username, 0, 1)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QLineEdit.Password)
        register_form_layout.addWidget(QLabel("Password:"), 1, 0)
        register_form_layout.addWidget(self.register_password, 1, 1)
        
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setPlaceholderText("Confirm Password")
        self.register_confirm_password.setEchoMode(QLineEdit.Password)
        register_form_layout.addWidget(QLabel("Confirm:"), 2, 0)
        register_form_layout.addWidget(self.register_confirm_password, 2, 1)
        
        register_button = QPushButton("Register User")
        register_button.clicked.connect(self.register_user)
        register_form_layout.addWidget(register_button, 3, 0, 1, 2)
        
        main_layout.addLayout(register_form_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def refresh_users(self) -> None:
        try:
            self.users = self.api_client.list_users()
            self.users_list.clear()
            
            for user in self.users:
                item_text = f"ID: {user['id']} - {user['username']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, user['id'])
                self.users_list.addItem(item)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(exc)}")
    
    def on_user_selected(self) -> None:
        current_item = self.users_list.currentItem()
        if current_item:
            user_id = current_item.data(Qt.UserRole)
            print(f"Selected user ID: {user_id}")
    
    def delete_selected_user(self) -> None:
        current_item = self.users_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a user to delete.")
            return
        
        user_id = current_item.data(Qt.UserRole)
        user_text = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {user_text}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.api_client.delete_user(user_id)
                QMessageBox.information(self, "Success", "User deleted successfully.")
                self.refresh_users()
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(exc)}")
    
    def register_user(self) -> None:
        username = self.register_username.text().strip()
        password = self.register_password.text().strip()
        confirm_password = self.register_confirm_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Username and password are required.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return
        
        try:
            self.api_client.create_user(username, password)
            QMessageBox.information(self, "Success", f"User '{username}' registered successfully.")
            
            # Clear form
            self.register_username.clear()
            self.register_password.clear()
            self.register_confirm_password.clear()
            
            # Refresh user list
            self.refresh_users()
        except Exception as exc:
            QMessageBox.critical(self, "Registration Failed", f"Error: {str(exc)}")

        