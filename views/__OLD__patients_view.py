# views/patients_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QLineEdit, QDialog, QFormLayout, QTextEdit,
                              QDateEdit, QComboBox, QMessageBox, QHeaderView,
                              QMenu, QGroupBox, QTabWidget, QSplitter, QCheckBox)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QIcon, QAction

import datetime
import json

from views.documents_view import PatientDocumentsView
from models.patient_manager import PatientManager
from views.patient_report_view import PatientReportDialog
from utils.validators import Validator
from utils.error_handler import ErrorHandler


class PatientDetailDialog(QDialog):
    """Dialog for viewing and editing patient details"""
    
    def __init__(self, patient_data=None, config_manager=None, parent=None):
        super().__init__(parent)
        
        self.patient_data = patient_data or {}
        self.config_manager = config_manager
        
        # Set dialog properties
        self.setWindowTitle("Patient Details")
        self.setMinimumSize(800, 600)
        
        # Setup UI
        self._setup_ui()
        
        # Load patient data if provided
        if patient_data:
            self._load_patient_data()
    
    # In PatientDetailDialog._setup_ui, add a new tab:
    def _setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Basic info tab
        self.basic_info_tab = QWidget()
        self._setup_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "Patient Information")
        
        # Medical history tab
        self.medical_history_tab = QWidget()
        self._setup_medical_history_tab()
        self.tab_widget.addTab(self.medical_history_tab, "Medical History")
        
        # Visit history tab
        self.visit_history_tab = QWidget()
        self._setup_visit_history_tab()
        self.tab_widget.addTab(self.visit_history_tab, "Visit History")
        
        # Medications tab (new)
        self.medications_tab = QWidget()
        self._setup_medications_tab()
        self.tab_widget.addTab(self.medications_tab, "Medications")
        
        # If you have test results and documents tabs
        if "test_results_tab" in dir(self):
            self.test_results_tab = QWidget()
            self._setup_test_results_tab()
            self.tab_widget.addTab(self.test_results_tab, "Test Results")
        
        if "documents_tab" in dir(self):
            self.documents_tab = QWidget()
            self._setup_documents_tab() 
            self.tab_widget.addTab(self.documents_tab, "Documents")
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Start visit button
        self.start_visit_btn = QPushButton("Start New Visit")
        self.start_visit_btn.clicked.connect(self._start_visit)
        buttons_layout.addWidget(self.start_visit_btn)
        
        # Add medical history button
        self.add_medical_btn = QPushButton("Add Medical Record")
        self.add_medical_btn.clicked.connect(self._add_medical_record)
        buttons_layout.addWidget(self.add_medical_btn)
        
        # Spacer
        buttons_layout.addStretch(1)
        
        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(buttons_layout)

    # Add new method to setup the medications tab:
    def _setup_medications_tab(self):
        """Set up the medications tab"""
        layout = QVBoxLayout(self.medications_tab)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        add_medication_btn = QPushButton("Add Medication")
        add_medication_btn.clicked.connect(self._add_medication)
        control_layout.addWidget(add_medication_btn)
        
        edit_medication_btn = QPushButton("Edit Selected")
        edit_medication_btn.clicked.connect(self._edit_medication)
        control_layout.addWidget(edit_medication_btn)
        
        delete_medication_btn = QPushButton("Delete Selected")
        delete_medication_btn.clicked.connect(self._delete_medication)
        control_layout.addWidget(delete_medication_btn)
        
        layout.addLayout(control_layout)
        
        # Medications table
        self.medications_table = QTableWidget()
        self.medications_table.setColumnCount(6)  # Name, Dosage, Frequency, Start Date, End Date, Notes
        self.medications_table.setHorizontalHeaderLabels(["Name", "Dosage", "Frequency", "Start Date", "End Date", "Notes"])
        self.medications_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.medications_table.setSelectionMode(QTableWidget.SingleSelection)
        self.medications_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.medications_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        self.medications_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Dosage
        self.medications_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Frequency
        self.medications_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Start Date
        self.medications_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # End Date
        self.medications_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Notes
        
        # Connect double-click signal
        self.medications_table.cellDoubleClicked.connect(self._edit_medication)
        
        layout.addWidget(self.medications_table)
        
        # Load medications if any
        self._load_medications()

    # Add method to load medications:
    def _load_medications(self):
        """Load medications into the table"""
        self.medications_table.setRowCount(0)
        
        medications = self.patient_data.get("medications", [])
        
        for row, medication in enumerate(sorted(medications, key=lambda x: x.get("name", ""))):
            self.medications_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(medication.get("name", ""))
            self.medications_table.setItem(row, 0, name_item)
            
            # Dosage
            dosage_item = QTableWidgetItem(medication.get("dosage", ""))
            self.medications_table.setItem(row, 1, dosage_item)
            
            # Frequency
            frequency_item = QTableWidgetItem(medication.get("frequency", ""))
            self.medications_table.setItem(row, 2, frequency_item)
            
            # Start Date
            start_date = medication.get("start_date", "")
            self.medications_table.setItem(row, 3, QTableWidgetItem(start_date))
            
            # End Date
            end_date = medication.get("end_date", "")
            self.medications_table.setItem(row, 4, QTableWidgetItem(end_date))
            
            # Notes
            notes_item = QTableWidgetItem(medication.get("notes", ""))
            self.medications_table.setItem(row, 5, notes_item)

    # Add method to add a new medication:
    def _add_medication(self):
        """Add a new medication"""
        if not self.patient_data:
            QMessageBox.warning(self, "Error", "Please save the patient first before adding medications.")
            return
        
        class MedicationDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                
                # Set dialog properties
                self.setWindowTitle("Add Medication")
                self.setMinimumWidth(400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                form_layout = QFormLayout()
                
                # Medication name
                self.name_edit = QLineEdit()
                self.name_edit.setPlaceholderText("Enter medication name")
                form_layout.addRow("Medication Name:", self.name_edit)
                
                # Dosage
                self.dosage_edit = QLineEdit()
                self.dosage_edit.setPlaceholderText("e.g., 10mg, 1 tablet")
                form_layout.addRow("Dosage:", self.dosage_edit)
                
                # Frequency
                self.frequency_edit = QLineEdit()
                self.frequency_edit.setPlaceholderText("e.g., Once daily, Twice daily")
                form_layout.addRow("Frequency:", self.frequency_edit)
                
                # Start Date
                self.start_date_edit = QDateEdit()
                self.start_date_edit.setCalendarPopup(True)
                self.start_date_edit.setDate(QDate.currentDate())
                form_layout.addRow("Start Date:", self.start_date_edit)
                
                # End Date (optional)
                self.end_date_edit = QDateEdit()
                self.end_date_edit.setCalendarPopup(True)
                self.end_date_edit.setDate(QDate.currentDate().addMonths(1))  # Default to 1 month later
                
                # Checkbox for ongoing medication
                self.ongoing_checkbox = QCheckBox("Ongoing medication (no end date)")
                self.ongoing_checkbox.toggled.connect(self._toggle_end_date)
                form_layout.addRow("", self.ongoing_checkbox)
                form_layout.addRow("End Date:", self.end_date_edit)
                
                # Notes
                self.notes_edit = QTextEdit()
                self.notes_edit.setPlaceholderText("Enter any additional notes about this medication")
                self.notes_edit.setMaximumHeight(100)
                form_layout.addRow("Notes:", self.notes_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("Add Medication")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
                
            def _toggle_end_date(self, checked):
                """Toggle the end date field based on checkbox state"""
                self.end_date_edit.setEnabled(not checked)
            
            def get_medication_data(self):
                """Get the medication data entered by the user"""
                medication_data = {
                    "name": self.name_edit.text(),
                    "dosage": self.dosage_edit.text(),
                    "frequency": self.frequency_edit.text(),
                    "start_date": self.start_date_edit.date().toString(Qt.ISODate),
                    "notes": self.notes_edit.toPlainText()
                }
                
                # Only include end date if not an ongoing medication
                if not self.ongoing_checkbox.isChecked():
                    medication_data["end_date"] = self.end_date_edit.date().toString(Qt.ISODate)
                
                return medication_data
        
        # Show the medication dialog
        dialog = MedicationDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get the medication data
            medication_data = dialog.get_medication_data()
            
            # Validate required fields
            if not medication_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Medication name is required.")
                return
            
            # Add to patient data
            if "medications" not in self.patient_data:
                self.patient_data["medications"] = []
            
            self.patient_data["medications"].append(medication_data)
            
            # Refresh the table
            self._load_medications()

    # Add method to edit an existing medication:
    def _edit_medication(self, row=None, column=None):
        """Edit an existing medication"""
        # Determine the selected row
        if row is None:
            selected_rows = self.medications_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "Selection Required", "Please select a medication to edit.")
                return
            row = selected_rows[0].row()
        
        # Get the medication data
        medications = self.patient_data.get("medications", [])
        if row >= len(medications):
            return
        
        medication_data = medications[row]
        
        class MedicationDialog(QDialog):
            def __init__(self, medication_data, parent=None):
                super().__init__(parent)
                self.medication_data = medication_data
                
                # Set dialog properties
                self.setWindowTitle("Edit Medication")
                self.setMinimumWidth(400)
                
                # Setup UI
                self._setup_ui()
                self._load_medication_data()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                form_layout = QFormLayout()
                
                # Medication name
                self.name_edit = QLineEdit()
                form_layout.addRow("Medication Name:", self.name_edit)
                
                # Dosage
                self.dosage_edit = QLineEdit()
                form_layout.addRow("Dosage:", self.dosage_edit)
                
                # Frequency
                self.frequency_edit = QLineEdit()
                form_layout.addRow("Frequency:", self.frequency_edit)
                
                # Start Date
                self.start_date_edit = QDateEdit()
                self.start_date_edit.setCalendarPopup(True)
                form_layout.addRow("Start Date:", self.start_date_edit)
                
                # End Date (optional)
                self.end_date_edit = QDateEdit()
                self.end_date_edit.setCalendarPopup(True)
                
                # Checkbox for ongoing medication
                self.ongoing_checkbox = QCheckBox("Ongoing medication (no end date)")
                self.ongoing_checkbox.toggled.connect(self._toggle_end_date)
                form_layout.addRow("", self.ongoing_checkbox)
                form_layout.addRow("End Date:", self.end_date_edit)
                
                # Notes
                self.notes_edit = QTextEdit()
                self.notes_edit.setMaximumHeight(100)
                form_layout.addRow("Notes:", self.notes_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("Save Changes")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
            
            def _load_medication_data(self):
                """Load the medication data into the form"""
                self.name_edit.setText(self.medication_data.get("name", ""))
                self.dosage_edit.setText(self.medication_data.get("dosage", ""))
                self.frequency_edit.setText(self.medication_data.get("frequency", ""))
                
                # Start date
                start_date_str = self.medication_data.get("start_date", "")
                if start_date_str:
                    try:
                        start_date = QDate.fromString(start_date_str, Qt.ISODate)
                        self.start_date_edit.setDate(start_date)
                    except:
                        self.start_date_edit.setDate(QDate.currentDate())
                else:
                    self.start_date_edit.setDate(QDate.currentDate())
                
                # End date
                end_date_str = self.medication_data.get("end_date", "")
                has_end_date = bool(end_date_str)
                
                if has_end_date:
                    try:
                        end_date = QDate.fromString(end_date_str, Qt.ISODate)
                        self.end_date_edit.setDate(end_date)
                    except:
                        self.end_date_edit.setDate(QDate.currentDate().addMonths(1))
                else:
                    self.end_date_edit.setDate(QDate.currentDate().addMonths(1))
                
                # Set the ongoing checkbox
                self.ongoing_checkbox.setChecked(not has_end_date)
                self.end_date_edit.setEnabled(has_end_date)
                
                # Notes
                self.notes_edit.setText(self.medication_data.get("notes", ""))
            
            def _toggle_end_date(self, checked):
                """Toggle the end date field based on checkbox state"""
                self.end_date_edit.setEnabled(not checked)
            
            def get_medication_data(self):
                """Get the medication data entered by the user"""
                medication_data = {
                    "name": self.name_edit.text(),
                    "dosage": self.dosage_edit.text(),
                    "frequency": self.frequency_edit.text(),
                    "start_date": self.start_date_edit.date().toString(Qt.ISODate),
                    "notes": self.notes_edit.toPlainText()
                }
                
                # Only include end date if not an ongoing medication
                if not self.ongoing_checkbox.isChecked():
                    medication_data["end_date"] = self.end_date_edit.date().toString(Qt.ISODate)
                
                return medication_data
        
        # Show the medication dialog
        dialog = MedicationDialog(medication_data, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get the updated medication data
            updated_data = dialog.get_medication_data()
            
            # Validate required fields
            if not updated_data["name"]:
                QMessageBox.warning(self, "Validation Error", "Medication name is required.")
                return
            
            # Update the medication in the list
            medications[row] = updated_data
            
            # Refresh the table
            self._load_medications()

# Add method to delete a medication:
    def _delete_medication(self):
        """Delete a medication"""
        selected_rows = self.medications_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select a medication to delete.")
            return
        
        row = selected_rows[0].row()
        
        # Get the medication name for the confirmation message
        medication_name = self.medications_table.item(row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete the medication '{medication_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from the list
            medications = self.patient_data.get("medications", [])
            if row < len(medications):
                del medications[row]
                
                # Refresh the table
                self._load_medications()
        
        
    # Add this new method to setup the documents tab:
    def _setup_documents_tab(self):
        """Set up the documents tab"""
        layout = QVBoxLayout(self.documents_tab)
        
        # Only create the documents view if we have a patient ID
        if self.patient_data and "id" in self.patient_data:
            self.documents_view = PatientDocumentsView(self.config_manager, self.patient_data["id"])
            layout.addWidget(self.documents_view)
        else:
            # Show a placeholder if no patient ID yet
            placeholder = QLabel("Save the patient first to manage documents")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder)

    # Add this new method to setup the test results tab:
    def _setup_test_results_tab(self):
        """Set up the test results tab"""
        layout = QVBoxLayout(self.test_results_tab)
        
        # Import this when you need it
        from views.test_results_view import PatientTestResultsView
        
        # Only create the test results view if we have a patient ID
        if self.patient_data and "id" in self.patient_data:
            self.test_results_view = PatientTestResultsView(self.config_manager, self.patient_data["id"])
            layout.addWidget(self.test_results_view)
        else:
            # Show a placeholder if no patient ID yet
            placeholder = QLabel("Save the patient first to manage test results")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder)
    
    def _setup_basic_info_tab(self):
        """Set up the basic information tab"""
        layout = QVBoxLayout(self.basic_info_tab)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Patient ID field (read-only if editing)
        self.id_edit = QLineEdit()
        if self.patient_data:  # Editing existing patient
            self.id_edit.setText(self.patient_data.get("id", ""))
            self.id_edit.setReadOnly(True)
        form_layout.addRow("Patient ID:", self.id_edit)
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter full name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Date of birth field
        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDate(QDate.currentDate().addYears(-30))  # Default to 30 years ago
        form_layout.addRow("Date of Birth:", self.dob_edit)
        
        # Gender field
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender_combo)
        
        # Contact information
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Enter phone number")
        form_layout.addRow("Phone:", self.phone_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email address")
        form_layout.addRow("Email:", self.email_edit)
        
        self.address_edit = QTextEdit()
        self.address_edit.setPlaceholderText("Enter full address")
        self.address_edit.setMaximumHeight(100)
        form_layout.addRow("Address:", self.address_edit)
        
        # Emergency contact
        self.emergency_name_edit = QLineEdit()
        self.emergency_name_edit.setPlaceholderText("Emergency contact name")
        form_layout.addRow("Emergency Contact:", self.emergency_name_edit)
        
        self.emergency_phone_edit = QLineEdit()
        self.emergency_phone_edit.setPlaceholderText("Emergency contact phone")
        form_layout.addRow("Emergency Phone:", self.emergency_phone_edit)
        
        # Insurance information
        self.insurance_provider_edit = QLineEdit()
        self.insurance_provider_edit.setPlaceholderText("Insurance provider name")
        form_layout.addRow("Insurance Provider:", self.insurance_provider_edit)
        
        self.insurance_id_edit = QLineEdit()
        self.insurance_id_edit.setPlaceholderText("Insurance ID/Policy number")
        form_layout.addRow("Insurance ID:", self.insurance_id_edit)
        
        # Notes field
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter any additional notes about the patient")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
    
    def _setup_medical_history_tab(self):
        """Set up the medical history tab"""
        layout = QVBoxLayout(self.medical_history_tab)
        
        # Medical history table
        self.medical_history_table = QTableWidget()
        self.medical_history_table.setColumnCount(5)  # Date, Type, Condition, Treatment, Notes
        self.medical_history_table.setHorizontalHeaderLabels(["Date", "Type", "Condition", "Treatment", "Notes"])
        self.medical_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.medical_history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.medical_history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.medical_history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        self.medical_history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        self.medical_history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Condition
        self.medical_history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Treatment
        self.medical_history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Notes
        
        layout.addWidget(self.medical_history_table)
    
    def _setup_visit_history_tab(self):
        """Set up the visit history tab"""
        layout = QVBoxLayout(self.visit_history_tab)
        
        # Visit history table
        self.visit_history_table = QTableWidget()
        self.visit_history_table.setColumnCount(6)  # Date, Doctor, Reason, Diagnosis, Treatment, Notes
        self.visit_history_table.setHorizontalHeaderLabels(["Date", "Doctor", "Reason", "Diagnosis", "Treatment", "Notes"])
        self.visit_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visit_history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.visit_history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.visit_history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        self.visit_history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Doctor
        self.visit_history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Reason
        self.visit_history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Diagnosis
        self.visit_history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Treatment
        self.visit_history_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Notes
        
        # Connect double-click signal to view visit details
        self.visit_history_table.cellDoubleClicked.connect(self._view_visit_details)
        
        layout.addWidget(self.visit_history_table)
    
    def _load_patient_data(self):
        """Load patient data into the form fields"""
        # Basic information
        self.id_edit.setText(self.patient_data.get("id", ""))
        self.name_edit.setText(self.patient_data.get("name", ""))
        
        # Date of birth
        dob_str = self.patient_data.get("dob", "")
        if dob_str:
            try:
                dob_date = QDate.fromString(dob_str, "yyyy-MM-dd")
                self.dob_edit.setDate(dob_date)
            except:
                pass
        
        # Gender
        gender = self.patient_data.get("gender", "")
        if gender in ["Male", "Female", "Other"]:
            self.gender_combo.setCurrentText(gender)
        
        # Contact information
        self.phone_edit.setText(self.patient_data.get("phone", ""))
        self.email_edit.setText(self.patient_data.get("email", ""))
        self.address_edit.setText(self.patient_data.get("address", ""))
        
        # Emergency contact
        self.emergency_name_edit.setText(self.patient_data.get("emergency_contact", {}).get("name", ""))
        self.emergency_phone_edit.setText(self.patient_data.get("emergency_contact", {}).get("phone", ""))
        
        # Insurance information
        self.insurance_provider_edit.setText(self.patient_data.get("insurance", {}).get("provider", ""))
        self.insurance_id_edit.setText(self.patient_data.get("insurance", {}).get("id", ""))
        
        # Notes
        self.notes_edit.setText(self.patient_data.get("notes", ""))
        
        # Load medical history
        self._load_medical_history()
        
        # Load visit history
        self._load_visit_history()
    
    def _load_medical_history(self):
        """Load medical history into the table"""
        self.medical_history_table.setRowCount(0)
        
        medical_history = self.patient_data.get("medical_history", [])
        
        for row, record in enumerate(sorted(medical_history, key=lambda x: x.get("date", ""), reverse=True)):
            self.medical_history_table.insertRow(row)
            
            # Date
            date_str = record.get("date", "")
            try:
                # Try to format the date nicely
                date_obj = datetime.datetime.fromisoformat(date_str)
                date_display = date_obj.strftime("%Y-%m-%d")
            except:
                date_display = date_str
                
            date_item = QTableWidgetItem(date_display)
            date_item.setData(Qt.UserRole, date_str)  # Store original date string
            self.medical_history_table.setItem(row, 0, date_item)
            
            # Type
            type_item = QTableWidgetItem(record.get("type", ""))
            self.medical_history_table.setItem(row, 1, type_item)
            
            # Condition
            condition_item = QTableWidgetItem(record.get("condition", ""))
            self.medical_history_table.setItem(row, 2, condition_item)
            
            # Treatment
            treatment_item = QTableWidgetItem(record.get("treatment", ""))
            self.medical_history_table.setItem(row, 3, treatment_item)
            
            # Notes
            notes_item = QTableWidgetItem(record.get("notes", ""))
            self.medical_history_table.setItem(row, 4, notes_item)
    
    def _load_visit_history(self):
        """Load visit history into the table"""
        self.visit_history_table.setRowCount(0)
        
        visit_history = self.patient_data.get("visit_history", [])
        
        for row, visit in enumerate(sorted(visit_history, key=lambda x: x.get("end_time", ""), reverse=True)):
            self.visit_history_table.insertRow(row)
            
            # Date (end time)
            date_str = visit.get("end_time", "")
            try:
                # Try to format the date nicely
                date_obj = datetime.datetime.fromisoformat(date_str)
                date_display = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                date_display = date_str
                
            date_item = QTableWidgetItem(date_display)
            date_item.setData(Qt.UserRole, visit)  # Store full visit data
            self.visit_history_table.setItem(row, 0, date_item)
            
            # Doctor
            doctor_item = QTableWidgetItem(visit.get("doctor", ""))
            self.visit_history_table.setItem(row, 1, doctor_item)
            
            # Reason
            reason_item = QTableWidgetItem(visit.get("reason", ""))
            self.visit_history_table.setItem(row, 2, reason_item)
            
            # Diagnosis
            diagnosis_item = QTableWidgetItem(visit.get("diagnosis", ""))
            self.visit_history_table.setItem(row, 3, diagnosis_item)
            
            # Treatment
            treatment_item = QTableWidgetItem(visit.get("treatment", ""))
            self.visit_history_table.setItem(row, 4, treatment_item)
            
            # Notes
            notes_item = QTableWidgetItem(visit.get("notes", ""))
            self.visit_history_table.setItem(row, 5, notes_item)
    
    def _start_visit(self):
        """Start a new visit for this patient"""
        if not self.patient_data:
            QMessageBox.warning(self, "Error", "Please save the patient first before starting a visit.")
            return
        
        class StartVisitDialog(QDialog):
            def __init__(self, config_manager, parent=None):
                super().__init__(parent)
                
                self.config_manager = config_manager
                
                # Set dialog properties
                self.setWindowTitle("Start New Visit")
                self.setMinimumWidth(400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                form_layout = QFormLayout()
                
                # Doctor selection
                self.doctor_combo = QComboBox()
                doctors = self.config_manager.config.get("doctors", [])
                self.doctor_combo.addItems(doctors)
                form_layout.addRow("Doctor:", self.doctor_combo)
                
                # Reason for visit
                self.reason_combo = QComboBox()
                self.reason_combo.setEditable(True)
                reasons = self.config_manager.config.get("visit_reasons", [])
                self.reason_combo.addItems(reasons)
                form_layout.addRow("Reason for Visit:", self.reason_combo)
                
                # Notes field
                self.notes_edit = QTextEdit()
                self.notes_edit.setPlaceholderText("Enter initial notes about the visit")
                self.notes_edit.setMaximumHeight(100)
                form_layout.addRow("Initial Notes:", self.notes_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("Start Visit")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
                
            def get_visit_data(self):
                """Get the visit data entered by the user"""
                return {
                    "doctor": self.doctor_combo.currentText(),
                    "reason": self.reason_combo.currentText(),
                    "notes": self.notes_edit.toPlainText()
                }
        
        # Show the start visit dialog
        dialog = StartVisitDialog(self.config_manager, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Signal the parent that we want to start a visit
            self.done(42)  # Using a custom result code
            
            # Store the visit data for parent to access
            self.visit_data = dialog.get_visit_data()
    
    
    def _add_medical_record(self):
        """Add a new medical record"""
        if not self.patient_data:
            QMessageBox.warning(self, "Error", "Please save the patient first before adding medical records.")
            return
        
        class AddMedicalRecordDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                
                # Set dialog properties
                self.setWindowTitle("Add Medical Record")
                self.setMinimumWidth(400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                form_layout = QFormLayout()
                
                # Record date
                self.date_edit = QDateEdit()
                self.date_edit.setCalendarPopup(True)
                self.date_edit.setDate(QDate.currentDate())
                form_layout.addRow("Date:", self.date_edit)
                
                # Type selection
                self.type_combo = QComboBox()
                self.type_combo.addItems([
                    "condition", "allergy", "surgery", "medication", "vaccination", "other"
                ])
                form_layout.addRow("Record Type:", self.type_combo)
                
                # Condition field
                self.condition_edit = QLineEdit()
                self.condition_edit.setPlaceholderText("Enter condition or diagnosis")
                form_layout.addRow("Condition:", self.condition_edit)
                
                # Treatment field
                self.treatment_edit = QTextEdit()
                self.treatment_edit.setPlaceholderText("Enter treatment or medications")
                self.treatment_edit.setMaximumHeight(100)
                form_layout.addRow("Treatment:", self.treatment_edit)
                
                # Notes field
                self.notes_edit = QTextEdit()
                self.notes_edit.setPlaceholderText("Enter additional notes")
                self.notes_edit.setMaximumHeight(100)
                form_layout.addRow("Notes:", self.notes_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("Add Record")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
                
            def get_medical_data(self):
                """Get the medical record data entered by the user"""
                return {
                    "type": self.type_combo.currentText(),
                    "condition": self.condition_edit.text(),
                    "treatment": self.treatment_edit.toPlainText(),
                    "notes": self.notes_edit.toPlainText(),
                    "date": self.date_edit.date().toString(Qt.ISODate)  # Use the date from the date picker
                }
        
        # Show the add medical record dialog
        dialog = AddMedicalRecordDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get the medical record data
            medical_data = dialog.get_medical_data()
            
            # Add to patient data
            if "medical_history" not in self.patient_data:
                self.patient_data["medical_history"] = []
            
            # Use the selected date instead of current timestamp
            # Note: We don't need to add a timestamp here since we're using the date from the date picker
            
            # Add to list
            self.patient_data["medical_history"].append(medical_data)
            
            # Refresh the table
            self._load_medical_history()
    
    def _view_visit_details(self, row, column):
        """View details of a selected visit"""
        # Get the visit data stored in the first column
        visit_data = self.visit_history_table.item(row, 0).data(Qt.UserRole)
        
        # Format dates nicely
        start_time = "Unknown"
        end_time = "Unknown"
        
        try:
            if "start_time" in visit_data:
                start_time_obj = datetime.datetime.fromisoformat(visit_data["start_time"])
                start_time = start_time_obj.strftime("%Y-%m-%d %H:%M")
            
            if "end_time" in visit_data:
                end_time_obj = datetime.datetime.fromisoformat(visit_data["end_time"])
                end_time = end_time_obj.strftime("%Y-%m-%d %H:%M")
        except:
            pass
        
        # Create detailed message
        details = f"Visit Details:\n\n"
        details += f"Date: {end_time}\n"
        details += f"Doctor: {visit_data.get('doctor', 'Unknown')}\n"
        details += f"Reason: {visit_data.get('reason', 'Unknown')}\n"
        details += f"Start Time: {start_time}\n"
        details += f"End Time: {end_time}\n\n"
        
        if visit_data.get("diagnosis"):
            details += f"Diagnosis: {visit_data['diagnosis']}\n\n"
        
        if visit_data.get("treatment"):
            details += f"Treatment: {visit_data['treatment']}\n\n"
        
        if visit_data.get("follow_up"):
            details += f"Follow-up: {visit_data['follow_up']}\n\n"
        
        if visit_data.get("notes"):
            details += f"Notes:\n{visit_data['notes']}\n"
        
        # Show details in a message box
        QMessageBox.information(self, "Visit Details", details)
    
    def get_patient_data(self):
        """Get the patient data from the form fields"""
        # Get basic information
        patient_id = self.id_edit.text().strip()
        name = self.name_edit.text().strip()
        
        # Validation
        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Patient ID is required.")
            return None
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Patient name is required.")
            return None
        
        # Validate email if provided
        if self.email_edit.text() and not Validator.validate_email(self.email_edit.text()):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address")
            return None
        
        # Validate phone if provided
        if self.phone_edit.text() and not Validator.validate_phone(self.phone_edit.text()):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid phone number")
            return None
            
        
        # Build patient data dictionary
        patient_data = self.patient_data.copy() if self.patient_data else {}
        
        patient_data["id"] = patient_id
        patient_data["name"] = name
        patient_data["dob"] = self.dob_edit.date().toString("yyyy-MM-dd")
        patient_data["gender"] = self.gender_combo.currentText()
        patient_data["phone"] = self.phone_edit.text()
        patient_data["email"] = self.email_edit.text()
        patient_data["address"] = self.address_edit.toPlainText()
        
        # Emergency contact
        patient_data["emergency_contact"] = {
            "name": self.emergency_name_edit.text(),
            "phone": self.emergency_phone_edit.text()
        }
        
        # Insurance information
        patient_data["insurance"] = {
            "provider": self.insurance_provider_edit.text(),
            "id": self.insurance_id_edit.text()
        }
        
        patient_data["notes"] = self.notes_edit.toPlainText()
        
        # Preserve existing medical history, visit history, and medications
        if "medical_history" not in patient_data:
            patient_data["medical_history"] = []
        
        if "visit_history" not in patient_data:
            patient_data["visit_history"] = []
        
        if "medications" not in patient_data:
            patient_data["medications"] = []
        
        return patient_data
    
    def _export_medical_report(self):
        """Export a medical report for the patient"""
        if not self.patient_data:
            QMessageBox.warning(self, "Error", "Please save the patient first.")
            return
        
        # Create and show report dialog
        dialog = PatientReportDialog(self.config_manager, self.patient_data, self)
        dialog.exec_()
    

class PatientsView(QWidget):
    """Main view for patient management"""
    
    def __init__(self, config_manager, current_user, user_role, error_handler=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        self.error_handler = error_handler or ErrorHandler(config_manager)
        
        # Create patient manager
        self.patient_manager = PatientManager(config_manager)
        
        # Setup UI
        self._setup_ui()
        
        # Load patients
        self.load_patients()
    
    def _setup_ui(self):
        """Set up the patients view UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title and actions
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Patient Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Search field
        search_label = QLabel("Search:")
        header_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search patients...")
        self.search_edit.setMaximumWidth(250)
        self.search_edit.textChanged.connect(self._filter_patients)
        header_layout.addWidget(self.search_edit)
        
        # Add spacer
        header_layout.addStretch(1)
        
        # Add patient button
        self.add_patient_btn = QPushButton("Add Patient")
        self.add_patient_btn.clicked.connect(self._add_patient)
        header_layout.addWidget(self.add_patient_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Patients table
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(7)  # ID, Name, Gender, Age/DOB, Phone, Email, Status
        self.patients_table.setHorizontalHeaderLabels(["ID", "Name", "Gender", "Age/DOB", "Phone", "Email", "Status"])
        self.patients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patients_table.setSelectionMode(QTableWidget.SingleSelection)
        self.patients_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.patients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        self.patients_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        self.patients_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Gender
        self.patients_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Age/DOB
        self.patients_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Phone
        self.patients_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # Email
        self.patients_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        
        # Connect double-click signal
        self.patients_table.cellDoubleClicked.connect(self._view_patient)
        
        # Connect context menu
        self.patients_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.patients_table.customContextMenuRequested.connect(self._show_context_menu)
        
        main_layout.addWidget(self.patients_table)
        
        # Status bar
        self.status_label = QLabel("0 patients")
        main_layout.addWidget(self.status_label)
    
    def load_patients(self):
        """Load patients into the table"""
        # Clear existing rows
        self.patients_table.setRowCount(0)
        
        # Get all patients
        patients = self.patient_manager.get_all_patients()
        
        # Add to table
        for row, (patient_id, patient_data) in enumerate(patients.items()):
            self.patients_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(patient_id)
            self.patients_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(patient_data.get("name", ""))
            self.patients_table.setItem(row, 1, name_item)
            
            # Gender
            gender_item = QTableWidgetItem(patient_data.get("gender", ""))
            self.patients_table.setItem(row, 2, gender_item)
            
            # Age/DOB
            dob_str = patient_data.get("dob", "")
            age_display = dob_str
            
            if dob_str:
                try:
                    dob_date = QDate.fromString(dob_str, "yyyy-MM-dd")
                    if dob_date.isValid():
                        # Calculate age
                        current_date = QDate.currentDate()
                        age = current_date.year() - dob_date.year()
                        
                        # Adjust if birthday hasn't occurred yet this year
                        if (current_date.month() < dob_date.month() or 
                            (current_date.month() == dob_date.month() and current_date.day() < dob_date.day())):
                            age -= 1
                        
                        age_display = f"{age} ({dob_str})"
                except:
                    pass
            
            age_item = QTableWidgetItem(age_display)
            self.patients_table.setItem(row, 3, age_item)
            
            # Phone
            phone_item = QTableWidgetItem(patient_data.get("phone", ""))
            self.patients_table.setItem(row, 4, phone_item)
            
            # Email
            email_item = QTableWidgetItem(patient_data.get("email", ""))
            self.patients_table.setItem(row, 5, email_item)
            
            # Status - check if patient has an active visit
            status = "Available"
            active_visits = self.patient_manager.get_all_active_visits()
            
            if patient_id in active_visits:
                status = "In Session"
            
            status_item = QTableWidgetItem(status)
            if status == "In Session":
                status_item.setForeground(Qt.red)
            self.patients_table.setItem(row, 6, status_item)
        
        # Update status bar
        self.status_label.setText(f"{len(patients)} patients")
    
    def _filter_patients(self):
        """Filter patients based on search text"""
        search_text = self.search_edit.text().lower()
        
        if not search_text:
            # Show all patients
            for row in range(self.patients_table.rowCount()):
                self.patients_table.setRowHidden(row, False)
            return
            
        # Search in ID, name, phone, and email columns
        for row in range(self.patients_table.rowCount()):
            id_item = self.patients_table.item(row, 0)
            name_item = self.patients_table.item(row, 1)
            gender_item = self.patients_table.item(row, 2)
            age_item = self.patients_table.item(row, 3)
            phone_item = self.patients_table.item(row, 4)
            email_item = self.patients_table.item(row, 5)
            
            # Check if search text is in any of the fields
            match_found = (
                search_text in id_item.text().lower() or
                search_text in name_item.text().lower() or
                search_text in gender_item.text().lower() or
                search_text in age_item.text().lower() or
                search_text in phone_item.text().lower() or
                search_text in email_item.text().lower()
            )
            
            self.patients_table.setRowHidden(row, not match_found)
        
        # Update status bar with visible count
        visible_count = sum(1 for row in range(self.patients_table.rowCount()) 
                           if not self.patients_table.isRowHidden(row))
        self.status_label.setText(f"{visible_count} of {self.patients_table.rowCount()} patients")
    
    def _add_patient(self):
        """Add a new patient"""
        try:
            # Create a unique patient ID
            new_id = f"P{len(self.patient_manager.get_all_patients()) + 1:04d}"
            
            # Show patient details dialog
            dialog = PatientDetailDialog({"id": new_id}, self.config_manager, self)
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                # Get patient data
                patient_data = dialog.get_patient_data()
                
                if patient_data:
                    # Add to patient manager
                    success, message = self.patient_manager.add_patient(patient_data)
                    
                    if success:
                        # Refresh table
                        self.load_patients()
                        
                        # Show success message
                        QMessageBox.information(self, "Success", f"Patient {patient_data['name']} added successfully.")
                    else:
                        # Show error message
                        QMessageBox.warning(self, "Error", f"Failed to add patient: {message}")
            elif result == 42:  # Custom result code for starting visit
                # Get patient data
                patient_data = dialog.get_patient_data()
                
                # Add patient first
                success, message = self.patient_manager.add_patient(patient_data)
                
                if success:
                    # Then start visit with the data from dialog
                    visit_data = dialog.visit_data
                    success, message = self.patient_manager.start_visit(patient_data["id"], visit_data)
                    
                    if success:
                        # Refresh table
                        self.load_patients()
                        
                        # Show success message
                        QMessageBox.information(self, "Success", f"Visit started for patient {patient_data['name']}.")
                    else:
                        # Show error message
                        QMessageBox.warning(self, "Error", f"Failed to start visit: {message}")
                else:
                    # Show error message
                    QMessageBox.warning(self, "Error", f"Failed to add patient: {message}")
        except Exception as e:
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_exception(e, "Adding new patient", parent=self)
            else:
                QMessageBox.critical(self, "Error", f"Failed to add patient: {str(e)}")
        
    def _view_patient(self, row, column):
        """View/edit patient details"""
        # Get patient ID from the table
        patient_id = self.patients_table.item(row, 0).text()
        
        # Get patient data
        patient_data = self.patient_manager.get_patient(patient_id)
        
        if not patient_data:
            QMessageBox.warning(self, "Error", f"Patient with ID {patient_id} not found.")
            return
        
        # Show patient details dialog
        dialog = PatientDetailDialog(patient_data, self.config_manager, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated patient data
            updated_data = dialog.get_patient_data()
            
            # Update in patient manager
            success, message = self.patient_manager.update_patient(patient_id, updated_data)
            
            if success:
                # Refresh table
                self.load_patients()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Patient {updated_data['name']} updated successfully.")
            else:
                # Show error message
                QMessageBox.warning(self, "Error", f"Failed to update patient: {message}")
        elif result == 42:  # Custom result code for starting visit
            # Start visit with the data from dialog
            visit_data = dialog.visit_data
            success, message = self.patient_manager.start_visit(patient_id, visit_data)
            
            if success:
                # Refresh table
                self.load_patients()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Visit started for patient {patient_data['name']}.")
            else:
                # Show error message
                QMessageBox.warning(self, "Error", f"Failed to start visit: {message}")
    
    def _show_context_menu(self, position):
        """Show context menu for patient table"""
        # Check if a row is selected
        indexes = self.patients_table.selectedIndexes()
        if not indexes:
            return
        
        # Get row and patient ID
        row = indexes[0].row()
        patient_id = self.patients_table.item(row, 0).text()
        patient_name = self.patients_table.item(row, 1).text()
        
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        view_action = QAction("View/Edit Patient", self)
        view_action.triggered.connect(lambda: self._view_patient(row, 0))
        menu.addAction(view_action)
        
        # Check if patient has an active visit
        active_visits = self.patient_manager.get_all_active_visits()
        
        if patient_id in active_visits:
            # Patient has an active visit - add end visit action
            end_visit_action = QAction("End Visit", self)
            end_visit_action.triggered.connect(lambda: self._end_visit(patient_id))
            menu.addAction(end_visit_action)
        else:
            # Patient doesn't have an active visit - add start visit action
            start_visit_action = QAction("Start Visit", self)
            start_visit_action.triggered.connect(lambda: self._start_visit(patient_id))
            menu.addAction(start_visit_action)
        
        menu.addSeparator()
        
        # Delete action - only for admin users
        if self.user_role == "admin":
            delete_action = QAction("Delete Patient", self)
            delete_action.triggered.connect(lambda: self._delete_patient(patient_id, patient_name))
            menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(self.patients_table.viewport().mapToGlobal(position))
    
    def _start_visit(self, patient_id):
        """Start a visit for a patient"""
        # Get patient data
        patient_data = self.patient_manager.get_patient(patient_id)
        
        if not patient_data:
            QMessageBox.warning(self, "Error", f"Patient with ID {patient_id} not found.")
            return
        
        class StartVisitDialog(QDialog):
            def __init__(self, config_manager, parent=None):
                super().__init__(parent)
                
                self.config_manager = config_manager
                
                # Set dialog properties
                self.setWindowTitle("Start New Visit")
                self.setMinimumWidth(400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                form_layout = QFormLayout()
                
                # Doctor selection
                self.doctor_combo = QComboBox()
                doctors = self.config_manager.config.get("doctors", [])
                self.doctor_combo.addItems(doctors)
                form_layout.addRow("Doctor:", self.doctor_combo)
                
                # Reason for visit
                self.reason_combo = QComboBox()
                self.reason_combo.setEditable(True)
                reasons = self.config_manager.config.get("visit_reasons", [])
                self.reason_combo.addItems(reasons)
                form_layout.addRow("Reason for Visit:", self.reason_combo)
                
                # Notes field
                self.notes_edit = QTextEdit()
                self.notes_edit.setPlaceholderText("Enter initial notes about the visit")
                self.notes_edit.setMaximumHeight(100)
                form_layout.addRow("Initial Notes:", self.notes_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("Start Visit")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
                
            def get_visit_data(self):
                """Get the visit data entered by the user"""
                return {
                    "doctor": self.doctor_combo.currentText(),
                    "reason": self.reason_combo.currentText(),
                    "notes": self.notes_edit.toPlainText()
                }
        
        # Show the start visit dialog
        dialog = StartVisitDialog(self.config_manager, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get visit data
            visit_data = dialog.get_visit_data()
            
            # Start visit
            success, message = self.patient_manager.start_visit(patient_id, visit_data)
            
            if success:
                # Refresh table
                self.load_patients()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Visit started for patient {patient_data['name']}.")
            else:
                # Show error message
                QMessageBox.warning(self, "Error", f"Failed to start visit: {message}")
    
    def _end_visit(self, patient_id):
        """End a visit for a patient"""
        # Get patient data
        patient_data = self.patient_manager.get_patient(patient_id)
        
        if not patient_data:
            QMessageBox.warning(self, "Error", f"Patient with ID {patient_id} not found.")
            return
        
        class EndVisitDialog(QDialog):
            def __init__(self, patient_data, active_visit, parent=None):
                super().__init__(parent)
                
                self.patient_data = patient_data
                self.active_visit = active_visit
                
                # Set dialog properties
                self.setWindowTitle("End Visit")
                self.setMinimumWidth(500)
                self.setMinimumHeight(400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                # Patient info
                info_layout = QHBoxLayout()
                info_layout.addWidget(QLabel(f"Patient: {self.patient_data.get('name', '')}"))
                info_layout.addWidget(QLabel(f"ID: {self.patient_data.get('id', '')}"))
                layout.addLayout(info_layout)
                
                # Visit info
                visit_layout = QHBoxLayout()
                doctor = self.active_visit.get("doctor", "Unknown")
                reason = self.active_visit.get("reason", "Unknown")
                
                visit_layout.addWidget(QLabel(f"Doctor: {doctor}"))
                visit_layout.addWidget(QLabel(f"Reason: {reason}"))
                layout.addLayout(visit_layout)
                
                # Form layout for visit notes
                form_layout = QFormLayout()
                
                # Notes field
                self.notes_edit = QTextEdit()
                original_notes = self.active_visit.get("notes", "")
                self.notes_edit.setText(original_notes)
                form_layout.addRow("Notes:", self.notes_edit)
                
                # Diagnosis field
                self.diagnosis_edit = QLineEdit()
                self.diagnosis_edit.setPlaceholderText("Enter diagnosis")
                form_layout.addRow("Diagnosis:", self.diagnosis_edit)
                
                # Treatment field
                self.treatment_edit = QTextEdit()
                self.treatment_edit.setPlaceholderText("Enter treatment plan")
                self.treatment_edit.setMaximumHeight(100)
                form_layout.addRow("Treatment:", self.treatment_edit)
                
                # Follow-up field
                self.follow_up_edit = QLineEdit()
                self.follow_up_edit.setPlaceholderText("Enter follow-up instructions")
                form_layout.addRow("Follow-up:", self.follow_up_edit)
                
                layout.addLayout(form_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                ok_button = QPushButton("End Visit")
                ok_button.clicked.connect(self.accept)
                buttons_layout.addWidget(ok_button)
                
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(cancel_button)
                
                layout.addLayout(buttons_layout)
                
            def get_visit_notes(self):
                """Get the visit notes entered by the user"""
                return {
                    "notes": self.notes_edit.toPlainText(),
                    "diagnosis": self.diagnosis_edit.text(),
                    "treatment": self.treatment_edit.toPlainText(),
                    "follow_up": self.follow_up_edit.text()
                }
        
        # Get active visit
        active_visit = self.patient_manager.get_active_visit(patient_id)
        
        if not active_visit:
            QMessageBox.warning(self, "Error", f"No active visit found for patient {patient_data['name']}.")
            return
        
        # Show the end visit dialog
        dialog = EndVisitDialog(patient_data, active_visit, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get visit notes
            visit_notes = dialog.get_visit_notes()
            
            # End visit
            success, message = self.patient_manager.end_visit(patient_id, visit_notes)
            
            if success:
                # Refresh table
                self.load_patients()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Visit ended for patient {patient_data['name']}.")
            else:
                # Show error message
                QMessageBox.warning(self, "Error", f"Failed to end visit: {message}")
    
    def _delete_patient(self, patient_id, patient_name):
        """Delete a patient"""
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete patient {patient_name}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Delete patient
        success, message = self.patient_manager.delete_patient(patient_id)
        
        if success:
            # Refresh table
            self.load_patients()
            
            # Show success message
            QMessageBox.information(self, "Success", f"Patient {patient_name} deleted successfully.")
        else:
            # Show error message
            QMessageBox.warning(self, "Error", f"Failed to delete patient: {message}")
    
    def refresh(self):
        """Refresh the view"""
        self.load_patients()