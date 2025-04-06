# views/login_window.py
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                              QLabel, QLineEdit, QCheckBox, QPushButton, 
                              QMessageBox)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QPixmap, QIcon

from utils.themes import apply_theme

class LoginWindow(QDialog):
    """Login dialog for user authentication"""
    
    login_successful = Signal(str, str)  # Signals username and role on success
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # Set window properties
        clinic_name = config_manager.config.get("clinic_name", "Medical Clinic")
        self.setWindowTitle(f"{clinic_name} - Login")
        
        # Try to load icon if available
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "assets", "icons", "clinic_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # Apply theme
        apply_theme(self)
        
        # Setup UI
        self._setup_ui()
        
        # Load saved username if available
        self._load_saved_credentials()
        
        # Track login attempts
        self.login_attempts = 0
        
        # Set initial focus
        self.username_edit.setFocus()
        
        
    def _setup_ui(self):
        """Create the login UI layout"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Logo/Header
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        
        # Try to load logo if available
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "assets", "icons", "clinic_icon.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        header_layout.addWidget(logo_label)
        
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        title_label = QLabel(clinic_name)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label, 1, Qt.AlignCenter)
        
        layout.addLayout(header_layout)
        
        # Form layout for login fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        layout.addWidget(self.remember_checkbox)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button)
        
        # Version info
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignRight)
        version_label.setStyleSheet("color: gray; font-size: 9px;")
        layout.addWidget(version_label)
    
    
    def _load_saved_credentials(self):
        """Load saved username if remember option was checked"""
        settings = QSettings("MedicalClinic", "AppSettings")
        self.remember_checkbox.setChecked(settings.value("remember_login", False, type=bool))
        
        if self.remember_checkbox.isChecked():
            self.username_edit.setText(settings.value("saved_username", ""))
    
    def _save_credentials(self, username):
        """Save username if remember option is checked"""
        settings = QSettings("MedicalClinic", "AppSettings")
        settings.setValue("remember_login", self.remember_checkbox.isChecked())
        
        if self.remember_checkbox.isChecked():
            settings.setValue("saved_username", username)
        else:
            settings.setValue("saved_username", "")
    
    def attempt_login(self):
        """Process login attempt"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return
        
        # Check for brute force protection
        if self.login_attempts >= 5:
            QMessageBox.critical(self, "Login Error", "Too many failed login attempts. Please try again later.")
            return
        
        # Attempt login
        user_data = self.config_manager.validate_login(username, password)
        
        if user_data:
            # Login successful
            self.login_attempts = 0
            self._save_credentials(username)
            
            # Emit signal with username and role
            self.login_successful.emit(username, user_data["role"])
            self.accept()
        else:
            # Login failed
            self.login_attempts += 1
            self.password_edit.clear()
            QMessageBox.warning(self, "Login Error", "Invalid username or password.")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.attempt_login()
        else:
            super().keyPressEvent(event)# views/login_window.py
