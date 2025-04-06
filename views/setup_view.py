# views/setup_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTabWidget, QFormLayout, QLineEdit,
                              QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
                              QSpinBox, QDoubleSpinBox, QGroupBox, QListWidget,
                              QListWidgetItem, QDialog, QDialogButtonBox, QInputDialog)
from PySide6.QtCore import Qt, Signal

class SetupView(QWidget):
    """Admin setup and configuration view"""
    
    def __init__(self, config_manager):
        super().__init__()
        
        self.config_manager = config_manager
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self._load_data()
    
    def _setup_ui(self):
        """Set up the setup view UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title
        header_layout = QHBoxLayout()
        
        title_label = QLabel("System Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._load_data)
        header_layout.addWidget(refresh_button)
        
        # Save button
        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self._save_all)
        header_layout.addWidget(save_button)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget for different setup areas
        self.tabs = QTabWidget()
        
        # Users tab
        self.users_tab = QWidget()
        self._setup_users_tab()
        self.tabs.addTab(self.users_tab, "Users")
        
        # Clinic Info tab
        self.clinic_tab = QWidget()
        self._setup_clinic_tab()
        self.tabs.addTab(self.clinic_tab, "Clinic Information")
        
        # Doctors tab
        self.doctors_tab = QWidget()
        self._setup_doctors_tab()
        self.tabs.addTab(self.doctors_tab, "Doctors")
        
        # Visit Reasons tab
        self.reasons_tab = QWidget()
        self._setup_reasons_tab()
        self.tabs.addTab(self.reasons_tab, "Visit Reasons")
        
        # System tab
        self.system_tab = QWidget()
        self._setup_system_tab()
        self.tabs.addTab(self.system_tab, "System")
        
        main_layout.addWidget(self.tabs)
    
    def _setup_users_tab(self):
        """Set up the users management tab"""
        layout = QVBoxLayout(self.users_tab)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self._add_user)
        control_layout.addWidget(add_user_btn)
        
        edit_user_btn = QPushButton("Edit Selected User")
        edit_user_btn.clicked.connect(self._edit_user)
        control_layout.addWidget(edit_user_btn)
        
        delete_user_btn = QPushButton("Delete Selected User")
        delete_user_btn.clicked.connect(self._delete_user)
        control_layout.addWidget(delete_user_btn)
        
        reset_password_btn = QPushButton("Reset Password")
        reset_password_btn.clicked.connect(self._reset_password)
        control_layout.addWidget(reset_password_btn)
        
        layout.addLayout(control_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)  # Username, Name, Role, Created On
        self.users_table.setHorizontalHeaderLabels(["Username", "Full Name", "Role", "Created On"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set column widths
        self.users_table.setColumnWidth(0, 150)  # Username
        self.users_table.setColumnWidth(1, 200)  # Full Name
        self.users_table.setColumnWidth(2, 100)  # Role
        self.users_table.setColumnWidth(3, 200)  # Created On
        
        layout.addWidget(self.users_table)
    
    def _setup_clinic_tab(self):
        """Set up the clinic information tab"""
        layout = QVBoxLayout(self.clinic_tab)
        
        form_layout = QFormLayout()
        
        # Clinic name
        self.clinic_name_edit = QLineEdit()
        form_layout.addRow("Clinic Name:", self.clinic_name_edit)
        
        # Address
        self.clinic_address_edit = QLineEdit()
        form_layout.addRow("Address:", self.clinic_address_edit)
        
        # Phone
        self.clinic_phone_edit = QLineEdit()
        form_layout.addRow("Phone:", self.clinic_phone_edit)
        
        # Email
        self.clinic_email_edit = QLineEdit()
        form_layout.addRow("Email:", self.clinic_email_edit)
        
        # Add to main layout
        layout.addLayout(form_layout)
        
        # Save button
        save_clinic_btn = QPushButton("Save Clinic Information")
        save_clinic_btn.clicked.connect(self._save_clinic_info)
        layout.addWidget(save_clinic_btn)
        
        # Add spacer
        layout.addStretch(1)
    
    def _setup_doctors_tab(self):
        """Set up the doctors management tab"""
        layout = QVBoxLayout(self.doctors_tab)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        add_doctor_btn = QPushButton("Add Doctor")
        add_doctor_btn.clicked.connect(self._add_doctor)
        control_layout.addWidget(add_doctor_btn)
        
        edit_doctor_btn = QPushButton("Edit Selected")
        edit_doctor_btn.clicked.connect(self._edit_doctor)
        control_layout.addWidget(edit_doctor_btn)
        
        delete_doctor_btn = QPushButton("Delete Selected")
        delete_doctor_btn.clicked.connect(self._delete_doctor)
        control_layout.addWidget(delete_doctor_btn)
        
        layout.addLayout(control_layout)
        
        # Doctors list
        self.doctors_list = QListWidget()
        self.doctors_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.doctors_list)
    
    def _setup_reasons_tab(self):
        """Set up the visit reasons tab"""
        layout = QVBoxLayout(self.reasons_tab)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        add_reason_btn = QPushButton("Add Reason")
        add_reason_btn.clicked.connect(self._add_reason)
        control_layout.addWidget(add_reason_btn)
        
        edit_reason_btn = QPushButton("Edit Selected")
        edit_reason_btn.clicked.connect(self._edit_reason)
        control_layout.addWidget(edit_reason_btn)
        
        delete_reason_btn = QPushButton("Delete Selected")
        delete_reason_btn.clicked.connect(self._delete_reason)
        control_layout.addWidget(delete_reason_btn)
        
        layout.addLayout(control_layout)
        
        # Reasons list
        self.reasons_list = QListWidget()
        self.reasons_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.reasons_list)
    
    def _setup_system_tab(self):
        """Set up the system configuration tab"""
        layout = QVBoxLayout(self.system_tab)
        
        # Backup controls
        backup_group = QGroupBox("Data Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_btn = QPushButton("Create Manual Backup")
        backup_btn.clicked.connect(self._create_backup)
        backup_layout.addWidget(backup_btn)
        
        layout.addWidget(backup_group)
        
        # Archive controls
        archive_group = QGroupBox("Visit History")
        archive_layout = QVBoxLayout(archive_group)
        
        archive_btn = QPushButton("Archive Old Visits")
        archive_btn.setToolTip("Archive visits older than 90 days")
        archive_btn.clicked.connect(self._archive_visits)
        archive_layout.addWidget(archive_btn)
        
        layout.addWidget(archive_group)
        
        # Reset system
        reset_group = QGroupBox("System Reset")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_system_button = QPushButton("Reset Complete System")
        reset_system_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        reset_system_button.clicked.connect(self._reset_complete_system)
        reset_layout.addWidget(reset_system_button)
        
        reset_warning = QLabel("WARNING: This will delete ALL patient data, visit history, and user accounts (except admin)!")
        reset_warning.setStyleSheet("color: red;")
        reset_warning.setWordWrap(True)
        reset_layout.addWidget(reset_warning)
        
        layout.addWidget(reset_group)
        
        # Add spacer at the bottom
        layout.addStretch(1)
    
    def _load_data(self):
        """Load data from config into UI"""
        self._load_users()
        self._load_clinic_info()
        self._load_doctors()
        self._load_reasons()
    
    def _load_users(self):
        """Load users data into the users table"""
        # Clear existing data
        self.users_table.setRowCount(0)
        
        # Get users from config
        users = self.config_manager.get_all_users()
        
        # Populate table
        for row, (username, user_data) in enumerate(users.items()):
            self.users_table.insertRow(row)
            
            # Username
            username_item = QTableWidgetItem(username)
            username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.users_table.setItem(row, 0, username_item)
            
            # Full Name
            name_item = QTableWidgetItem(user_data.get("name", ""))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.users_table.setItem(row, 1, name_item)
            
            # Role
            role_item = QTableWidgetItem(user_data.get("role", "user"))
            role_item.setFlags(role_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.users_table.setItem(row, 2, role_item)
            
            # Created on
            created_on = user_data.get("created_on", "Unknown")
            created_item = QTableWidgetItem(created_on)
            created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.users_table.setItem(row, 3, created_item)
        
        # Resize to content
        self.users_table.resizeColumnsToContents()
    
    def _load_clinic_info(self):
        """Load clinic information into the form"""
        self.clinic_name_edit.setText(self.config_manager.config.get("clinic_name", "Medical Clinic"))
        self.clinic_address_edit.setText(self.config_manager.config.get("clinic_address", ""))
        self.clinic_phone_edit.setText(self.config_manager.config.get("clinic_phone", ""))
        self.clinic_email_edit.setText(self.config_manager.config.get("clinic_email", ""))
    
    def _load_doctors(self):
        """Load doctors into the list"""
        # Clear existing data
        self.doctors_list.clear()
        
        # Get doctors from config
        doctors = self.config_manager.config.get("doctors", [])
        
        # Add to list
        for doctor in doctors:
            self.doctors_list.addItem(doctor)
    
    def _load_reasons(self):
        """Load visit reasons into the list"""
        # Clear existing data
        self.reasons_list.clear()
        
        # Get reasons from config
        reasons = self.config_manager.config.get("visit_reasons", [])
        
        # Add to list
        for reason in reasons:
            self.reasons_list.addItem(reason)
    
    def _add_user(self):
        """Add a new user"""
        # Create add user dialog
        class AddUserDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Add New User")
                self.setMinimumWidth(300)
                
                layout = QVBoxLayout(self)
                
                # Form layout
                form_layout = QFormLayout()
                
                self.username_edit = QLineEdit()
                form_layout.addRow("Username:", self.username_edit)
                
                self.name_edit = QLineEdit()
                form_layout.addRow("Full Name:", self.name_edit)
                
                self.password_edit = QLineEdit()
                self.password_edit.setEchoMode(QLineEdit.Password)
                form_layout.addRow("Password:", self.password_edit)
                
                self.confirm_password_edit = QLineEdit()
                self.confirm_password_edit.setEchoMode(QLineEdit.Password)
                form_layout.addRow("Confirm Password:", self.confirm_password_edit)
                
                self.role_combo = QComboBox()
                self.role_combo.addItems(["user", "admin"])
                form_layout.addRow("Role:", self.role_combo)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttons.accepted.connect(self.accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)
                
        dialog = AddUserDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            username = dialog.username_edit.text().strip()
            full_name = dialog.name_edit.text().strip()
            password = dialog.password_edit.text()
            confirm_password = dialog.confirm_password_edit.text()
            role = dialog.role_combo.currentText()
            
            # Validate inputs
            if not username:
                QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
                return
            
            if not password:
                QMessageBox.warning(self, "Input Error", "Password cannot be empty.")
                return
            
            if password != confirm_password:
                QMessageBox.warning(self, "Input Error", "Passwords do not match.")
                return
            
            # Add user via config manager
            success, message = self.config_manager.add_user(username, password, role, full_name)
            
            if success:
                QMessageBox.information(self, "User Added", 
                                       f"User '{username}' has been added successfully.")
                self._load_users()  # Refresh user list
            else:
                QMessageBox.warning(self, "Error", f"Failed to add user: {message}")
    
    def _edit_user(self):
        """Edit the selected user's role and name"""
        selected_items = self.users_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return
        
        row = selected_items[0].row()
        username = self.users_table.item(row, 0).text()
        current_name = self.users_table.item(row, 1).text()
        current_role = self.users_table.item(row, 2).text()
        
        # Cannot edit the admin user's role
        is_admin = (username == "admin")
        
        # Create edit user dialog
        class EditUserDialog(QDialog):
            def __init__(self, username, current_name, current_role, is_admin, parent=None):
                super().__init__(parent)
                self.setWindowTitle(f"Edit User: {username}")
                self.setMinimumWidth(300)
                
                layout = QVBoxLayout(self)
                
                # Form layout
                form_layout = QFormLayout()
                
                # Username (display only)
                username_label = QLabel(username)
                form_layout.addRow("Username:", username_label)
                
                # Full name
                self.name_edit = QLineEdit(current_name)
                form_layout.addRow("Full Name:", self.name_edit)
                
                # Role
                self.role_combo = QComboBox()
                self.role_combo.addItems(["user", "admin"])
                index = self.role_combo.findText(current_role)
                self.role_combo.setCurrentIndex(index if index >= 0 else 0)
                
                # Disable role change for admin user
                if is_admin:
                    self.role_combo.setEnabled(False)
                    
                form_layout.addRow("Role:", self.role_combo)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttons.accepted.connect(self.accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)
                
        dialog = EditUserDialog(username, current_name, current_role, is_admin, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            new_name = dialog.name_edit.text().strip()
            new_role = dialog.role_combo.currentText()
            
            # Update user in config manager
            # Since there's no direct method to update name and role, we'll need to modify users directly
            if username in self.config_manager.users:
                if not is_admin or new_role == "admin":  # Prevent changing admin's role
                    self.config_manager.users[username]["role"] = new_role
                self.config_manager.users[username]["name"] = new_name
                
                success = self.config_manager.save_users()
                
                if success:
                    QMessageBox.information(self, "User Updated", 
                                          f"User '{username}' has been updated successfully.")
                    self._load_users()  # Refresh user list
                else:
                    QMessageBox.warning(self, "Error", "Failed to update user.")
            else:
                QMessageBox.warning(self, "Error", f"User '{username}' not found.")
    
    def _delete_user(self):
        """Delete the selected user"""
        selected_items = self.users_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return
        
        row = selected_items[0].row()
        username = self.users_table.item(row, 0).text()
        
        # Cannot delete the admin user
        if username == "admin":
            QMessageBox.warning(self, "Delete Restricted", 
                              "The main admin user cannot be deleted.")
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Delete user via config manager
        success, message = self.config_manager.delete_user(username)
        
        if success:
            QMessageBox.information(self, "User Deleted", 
                                  f"User '{username}' has been deleted.")
            self._load_users()  # Refresh user list
        else:
            QMessageBox.warning(self, "Error", f"Failed to delete user: {message}")
    
    def _reset_password(self):
        """Reset password for the selected user"""
        selected_items = self.users_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a user to reset password.")
            return
        
        row = selected_items[0].row()
        username = self.users_table.item(row, 0).text()
        
        # Create password reset dialog
        class PasswordResetDialog(QDialog):
            def __init__(self, username, parent=None):
                super().__init__(parent)
                self.setWindowTitle(f"Reset Password for {username}")
                self.setMinimumWidth(300)
                
                layout = QVBoxLayout(self)
                
                # Form layout
                form_layout = QFormLayout()
                
                self.new_password_edit = QLineEdit()
                self.new_password_edit.setEchoMode(QLineEdit.Password)
                form_layout.addRow("New Password:", self.new_password_edit)
                
                self.confirm_password_edit = QLineEdit()
                self.confirm_password_edit.setEchoMode(QLineEdit.Password)
                form_layout.addRow("Confirm Password:", self.confirm_password_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttons.accepted.connect(self.accept)
                buttons.rejected.connect(self.reject)
                layout.addWidget(buttons)
                
        dialog = PasswordResetDialog(username, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            new_password = dialog.new_password_edit.text()
            confirm_password = dialog.confirm_password_edit.text()
            
            # Validate inputs
            if not new_password:
                QMessageBox.warning(self, "Input Error", "Password cannot be empty.")
                return
            
            if new_password != confirm_password:
                QMessageBox.warning(self, "Input Error", "Passwords do not match.")
                return
            
            # Change password via config manager
            success, message = self.config_manager.change_password(username, new_password)
            
            if success:
                QMessageBox.information(self, "Password Reset", 
                                      f"Password for user '{username}' has been reset.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to reset password: {message}")
    
    def _save_clinic_info(self):
        """Save clinic information to config"""
        # Get values from form
        clinic_name = self.clinic_name_edit.text().strip()
        clinic_address = self.clinic_address_edit.text().strip()
        clinic_phone = self.clinic_phone_edit.text().strip()
        clinic_email = self.clinic_email_edit.text().strip()
        
        # Validate input
        if not clinic_name:
            QMessageBox.warning(self, "Input Error", "Clinic name cannot be empty.")
            return
        
        # Update config
        self.config_manager.config["clinic_name"] = clinic_name
        self.config_manager.config["clinic_address"] = clinic_address
        self.config_manager.config["clinic_phone"] = clinic_phone
        self.config_manager.config["clinic_email"] = clinic_email
        
        # Save config
        success = self.config_manager.save_config()
        
        if success:
            QMessageBox.information(self, "Success", "Clinic information has been updated.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save clinic information.")
    
    def _add_doctor(self):
        """Add a new doctor to the list"""
        # Ask for doctor name
        doctor_name, ok = QInputDialog.getText(
            self, "Add Doctor", "Enter doctor name:")
        
        if not ok or not doctor_name:
            return
        
        # Add to config
        doctors = self.config_manager.config.get("doctors", [])
        
        if doctor_name in doctors:
            QMessageBox.warning(self, "Input Error", f"Doctor '{doctor_name}' already exists.")
            return
        
        doctors.append(doctor_name)
        self.config_manager.config["doctors"] = doctors
        
        # Save config
        success = self.config_manager.save_config()
        
        if success:
            QMessageBox.information(self, "Success", f"Doctor '{doctor_name}' has been added.")
            self._load_doctors()  # Refresh list
        else:
            QMessageBox.warning(self, "Error", "Failed to save doctor information.")
    
    def _edit_doctor(self):
        """Edit the selected doctor"""
        # Get selected doctor
        selected_items = self.doctors_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to edit.")
            return
        
        current_name = selected_items[0].text()
        
        # Ask for new name
        new_name, ok = QInputDialog.getText(
            self, "Edit Doctor", "Enter new name:",
            text=current_name)
        
        if not ok or not new_name or new_name == current_name:
            return
        
        # Update in config
        doctors = self.config_manager.config.get("doctors", [])
        
        if new_name in doctors:
            QMessageBox.warning(self, "Input Error", f"Doctor '{new_name}' already exists.")
            return
        
        # Replace in list
        index = doctors.index(current_name)
        doctors[index] = new_name
        
        # Save config
        success = self.config_manager.save_config()
        
        if success:
            QMessageBox.information(self, "Success", f"Doctor name has been updated.")
            self._load_doctors()  # Refresh list
        else:
            QMessageBox.warning(self, "Error", "Failed to save doctor information.")
    
    def _delete_doctor(self):
        """Delete the selected doctor"""
        # Get selected doctor
        selected_items = self.doctors_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to delete.")
            return
        
        doctor_name = selected_items[0].text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete doctor '{doctor_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Remove from config
        doctors = self.config_manager.config.get("doctors", [])
        
        if doctor_name in doctors:
            doctors.remove(doctor_name)
            self.config_manager.config["doctors"] = doctors
            
            # Save config
            success = self.config_manager.save_config()
            
            if success:
                QMessageBox.information(self, "Success", f"Doctor '{doctor_name}' has been deleted.")
                self._load_doctors()  # Refresh list
            else:
                QMessageBox.warning(self, "Error", "Failed to save changes.")
        else:
            QMessageBox.warning(self, "Error", f"Doctor '{doctor_name}' not found.")
    
    def _add_reason(self):
        """Add a new visit reason to the list"""
        # Ask for reason
        reason, ok = QInputDialog.getText(
            self, "Add Visit Reason", "Enter visit reason:")
        
        if not ok or not reason:
            return
        
        # Add to config
        reasons = self.config_manager.config.get("visit_reasons", [])
        
        if reason in reasons:
            QMessageBox.warning(self, "Input Error", f"Reason '{reason}' already exists.")
            return
        
        reasons.append(reason)
        self.config_manager.config["visit_reasons"] = reasons
        
        # Save config
        success = self.config_manager.save_config()
        
        if success:
            QMessageBox.information(self, "Success", f"Visit reason '{reason}' has been added.")
            self._load_reasons()  # Refresh list
        else:
            QMessageBox.warning(self, "Error", "Failed to save changes.")
    
    def _edit_reason(self):
        """Edit the selected visit reason"""
        # Get selected reason
        selected_items = self.reasons_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a reason to edit.")
            return
        
        current_reason = selected_items[0].text()
        
        # Ask for new reason
        new_reason, ok = QInputDialog.getText(
            self, "Edit Visit Reason", "Enter new reason:",
            text=current_reason)
        
        if not ok or not new_reason or new_reason == current_reason:
            return
        
        # Update in config
        reasons = self.config_manager.config.get("visit_reasons", [])
        
        if new_reason in reasons:
            QMessageBox.warning(self, "Input Error", f"Reason '{new_reason}' already exists.")
            return
        
        # Replace in list
        index = reasons.index(current_reason)
        reasons[index] = new_reason
        
        # Save config
        success = self.config_manager.save_config()
        
        if success:
            QMessageBox.information(self, "Success", f"Visit reason has been updated.")
            self._load_reasons()  # Refresh list
        else:
            QMessageBox.warning(self, "Error", "Failed to save changes.")
    
    def _delete_reason(self):
        """Delete the selected visit reason"""
        # Get selected reason
        selected_items = self.reasons_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a reason to delete.")
            return
        
        reason = selected_items[0].text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete reason '{reason}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Remove from config
        reasons = self.config_manager.config.get("visit_reasons", [])
        
        if reason in reasons:
            reasons.remove(reason)
            self.config_manager.config["visit_reasons"] = reasons
            
            # Save config
            success = self.config_manager.save_config()
            
            if success:
                QMessageBox.information(self, "Success", f"Reason '{reason}' has been deleted.")
                self._load_reasons()  # Refresh list
            else:
                QMessageBox.warning(self, "Error", "Failed to save changes.")
        else:
            QMessageBox.warning(self, "Error", f"Reason '{reason}' not found.")
    
    def _create_backup(self):
        """Create a manual backup of configuration files"""
        try:
            success = self.config_manager.create_manual_backup()
            if success:
                QMessageBox.information(self, "Backup Created", "Manual backup created successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to create backup.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def _archive_visits(self):
        """Archive old visit records"""
        confirm = QMessageBox.question(
            self, "Confirm Archiving",
            "This will archive visits older than 90 days to reduce system load. "
            "The data will still be available for reports. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        try:
            success, message = self.config_manager.archive_old_visits(days=90)
            
            if success:
                QMessageBox.information(self, "Archive Complete", message)
            else:
                QMessageBox.warning(self, "Error", f"Failed to archive visits: {message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def _reset_complete_system(self):
        """Reset the entire system by clearing patient data and visits"""
        # Show a very clear warning
        confirm = QMessageBox.warning(
            self, "COMPLETE SYSTEM RESET",
            "WARNING: This will delete ALL patient data, visit histories, and all user accounts "
            "except the admin account!\n\n"
            "This action CANNOT be undone. This should only be used when setting up a new system "
            "or if there are critical data issues.\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default to No to prevent accidents
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Secondary confirmation with text entry
        text, ok = QInputDialog.getText(
            self, "Confirm System Reset",
            "Type 'RESET SYSTEM' (all caps) to confirm this irreversible action:"
        )
        
        if not ok or text != "RESET SYSTEM":
            QMessageBox.information(self, "Reset Cancelled", "System reset has been cancelled.")
            return
        
        # Perform the reset
        try:
            # Reset patients
            self.config_manager.config["patients"] = {}
            
            # Reset active visits
            self.config_manager.config["active_visits"] = {}
            
            # Reset archived visits
            self.config_manager.config["archived_visits"] = {}
            
            # Save configuration
            success = self.config_manager.save_config()
            
            if success:
                QMessageBox.information(
                    self, "Reset Complete", 
                    "The system has been completely reset. All patient data and visit history has been cleared."
                )
            else:
                QMessageBox.warning(
                    self, "Error", 
                    "Failed to save the configuration after reset."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An error occurred during the system reset: {str(e)}"
            )
    
    def _save_all(self):
        """Save all changes to config"""
        # Save clinic info
        self._save_clinic_info()
        
        # Other sections save immediately when changed
        QMessageBox.information(self, "All Changes Saved", 
                              "All configuration changes have been saved.")
    
    def refresh(self):
        """Refresh the view (reload data)"""
        self._load_data()