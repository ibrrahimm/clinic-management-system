# views/active_visits_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QLineEdit, QDialog, QFormLayout, QTextEdit,
                              QDateEdit, QComboBox, QMessageBox, QHeaderView,
                              QMenu)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QIcon, QAction, QColor

import datetime

from models.patient_manager import PatientManager

class ActiveVisitsView(QWidget):
    """View displaying all active patient visits"""
    
    def __init__(self, config_manager, current_user, user_role):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        
        # Create patient manager
        self.patient_manager = PatientManager(config_manager)
        
        # Setup UI
        self._setup_ui()
        
        # Load active visits
        self.load_active_visits()
        
        # Setup auto-refresh timer (every 60 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_active_visits)
        self.refresh_timer.start(60000)  # 60 seconds
    
    def _setup_ui(self):
        """Set up the active visits view UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title and actions
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Active Visits")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Search field
        search_label = QLabel("Search:")
        header_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search active visits...")
        self.search_edit.setMaximumWidth(250)
        self.search_edit.textChanged.connect(self._filter_visits)
        header_layout.addWidget(self.search_edit)
        
        # Add spacer
        header_layout.addStretch(1)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Active visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(7)  # Patient ID, Patient Name, Doctor, Reason, Start Time, Duration, Actions
        self.visits_table.setHorizontalHeaderLabels(["Patient ID", "Patient Name", "Doctor", "Reason", "Start Time", "Duration", ""])
        self.visits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visits_table.setSelectionMode(QTableWidget.SingleSelection)
        self.visits_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.visits_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Patient ID
        self.visits_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Patient Name
        self.visits_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Doctor
        self.visits_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Reason
        self.visits_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Start Time
        self.visits_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Duration
        self.visits_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        # Connect double-click signal
        self.visits_table.cellDoubleClicked.connect(self._view_visit)
        
        # Connect context menu
        self.visits_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.visits_table.customContextMenuRequested.connect(self._show_context_menu)
        
        main_layout.addWidget(self.visits_table)
        
        # Status bar
        self.status_label = QLabel("0 active visits")
        main_layout.addWidget(self.status_label)
    
    def load_active_visits(self):
        """Load active visits into the table"""
        # Clear existing rows
        self.visits_table.setRowCount(0)
        
        # Get all active visits
        active_visits = self.patient_manager.get_all_active_visits()
        
        # Add to table
        for row, (patient_id, visit_info) in enumerate(active_visits.items()):
            patient_name = visit_info.get("patient_name", "Unknown")
            visit_data = visit_info.get("visit_data", {})
            
            self.visits_table.insertRow(row)
            
            # Patient ID
            id_item = QTableWidgetItem(patient_id)
            self.visits_table.setItem(row, 0, id_item)
            
            # Patient Name
            name_item = QTableWidgetItem(patient_name)
            self.visits_table.setItem(row, 1, name_item)
            
            # Doctor
            doctor_item = QTableWidgetItem(visit_data.get("doctor", "Unknown"))
            self.visits_table.setItem(row, 2, doctor_item)
            
            # Reason
            reason_item = QTableWidgetItem(visit_data.get("reason", "Unknown"))
            self.visits_table.setItem(row, 3, reason_item)
            
            # Start Time
            start_time = visit_data.get("start_time")
            start_time_str = "Unknown"
            
            if start_time:
                if isinstance(start_time, str):
                    try:
                        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                
                if isinstance(start_time, datetime.datetime):
                    start_time_str = start_time.strftime("%Y-%m-%d %H:%M")
            
            start_time_item = QTableWidgetItem(start_time_str)
            start_time_item.setData(Qt.UserRole, start_time)  # Store datetime object for sorting
            self.visits_table.setItem(row, 4, start_time_item)
            
            # Duration
            duration_str = "Unknown"
            
            if isinstance(start_time, datetime.datetime):
                # Calculate duration
                duration = datetime.datetime.now() - start_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                duration_str = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
                
                # Color code duration based on time
                if hours >= 2:
                    # Long visit - red
                    color = QColor(255, 200, 200)
                elif hours >= 1:
                    # Medium visit - yellow
                    color = QColor(255, 255, 200)
                else:
                    # Short visit - green
                    color = QColor(200, 255, 200)
            
            duration_item = QTableWidgetItem(duration_str)
            if isinstance(start_time, datetime.datetime):
                duration_item.setBackground(color)
            self.visits_table.setItem(row, 5, duration_item)
            
            # Actions - create frame with multiple buttons
            actions_frame = QFrame()
            actions_layout = QHBoxLayout(actions_frame)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(4)
            
            # End visit button - make it more prominent
            end_visit_btn = QPushButton("End Visit")
            end_visit_btn.setProperty("patient_id", patient_id)
            end_visit_btn.clicked.connect(self._end_visit_clicked)
            # Make button more prominent with styling
            end_visit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            end_visit_btn.setMinimumWidth(100)
            actions_layout.addWidget(end_visit_btn)
            
            # Add view button 
            view_btn = QPushButton("View")
            view_btn.setProperty("patient_id", patient_id)
            view_btn.setProperty("row", row)
            view_btn.clicked.connect(lambda checked, r=row: self._view_visit(r, 0))
            actions_layout.addWidget(view_btn)
            
            self.visits_table.setCellWidget(row, 6, actions_frame)
        
        # Update status bar
        self.status_label.setText(f"{len(active_visits)} active visits")
    
    def _filter_visits(self):
        """Filter visits based on search text"""
        search_text = self.search_edit.text().lower()
        
        if not search_text:
            # Show all visits
            for row in range(self.visits_table.rowCount()):
                self.visits_table.setRowHidden(row, False)
            return
            
        # Search in patient ID, name, doctor, and reason columns
        for row in range(self.visits_table.rowCount()):
            id_item = self.visits_table.item(row, 0)
            name_item = self.visits_table.item(row, 1)
            doctor_item = self.visits_table.item(row, 2)
            reason_item = self.visits_table.item(row, 3)
            
            # Check if search text is in any of the fields
            match_found = (
                search_text in id_item.text().lower() or
                search_text in name_item.text().lower() or
                search_text in doctor_item.text().lower() or
                search_text in reason_item.text().lower()
            )
            
            self.visits_table.setRowHidden(row, not match_found)
        
        # Update status bar with visible count
        visible_count = sum(1 for row in range(self.visits_table.rowCount()) 
                           if not self.visits_table.isRowHidden(row))
        self.status_label.setText(f"{visible_count} of {self.visits_table.rowCount()} active visits")
    
    def _view_visit(self, row, column):
        """View details of a visit and update notes"""
        # Get patient ID
        patient_id = self.visits_table.item(row, 0).text()
        patient_name = self.visits_table.item(row, 1).text()
        
        # Get active visit
        active_visit = self.patient_manager.get_active_visit(patient_id)
        
        if not active_visit:
            QMessageBox.warning(self, "Error", "Visit information not found.")
            return
        
        class VisitDetailsDialog(QDialog):
            def __init__(self, patient_id, patient_name, visit_data, parent=None):
                super().__init__(parent)
                
                self.patient_id = patient_id
                self.patient_name = patient_name
                self.visit_data = visit_data
                
                # Set dialog properties
                self.setWindowTitle(f"Visit Details - {patient_name}")
                self.setMinimumSize(500, 400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                # Visit information
                info_group = QFormLayout()
                
                # Patient info
                info_group.addRow("Patient:", QLabel(f"{self.patient_name} (ID: {self.patient_id})"))
                
                # Doctor
                info_group.addRow("Doctor:", QLabel(self.visit_data.get("doctor", "Unknown")))
                
                # Reason
                info_group.addRow("Reason:", QLabel(self.visit_data.get("reason", "Unknown")))
                
                # Start time
                start_time = self.visit_data.get("start_time")
                start_time_str = "Unknown"
                
                if start_time:
                    if isinstance(start_time, str):
                        try:
                            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass
                    
                    if isinstance(start_time, datetime.datetime):
                        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                
                info_group.addRow("Start Time:", QLabel(start_time_str))
                
                # Duration
                if isinstance(start_time, datetime.datetime):
                    # Calculate duration
                    duration = datetime.datetime.now() - start_time
                    hours, remainder = divmod(duration.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    duration_str = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
                    info_group.addRow("Duration:", QLabel(duration_str))
                
                layout.addLayout(info_group)
                
                # Separator
                separator = QLabel()
                separator.setFrameStyle(QLabel.HLine | QLabel.Sunken)
                layout.addWidget(separator)
                
                # Notes
                notes_label = QLabel("Visit Notes:")
                layout.addWidget(notes_label)
                
                self.notes_edit = QTextEdit()
                self.notes_edit.setText(self.visit_data.get("notes", ""))
                layout.addWidget(self.notes_edit)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                
                self.save_button = QPushButton("Update Notes")
                self.save_button.clicked.connect(self.accept)
                buttons_layout.addWidget(self.save_button)
                
                self.end_visit_button = QPushButton("End Visit")
                self.end_visit_button.clicked.connect(lambda: self.done(42))  # Custom result code
                buttons_layout.addWidget(self.end_visit_button)
                
                self.cancel_button = QPushButton("Cancel")
                self.cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(self.cancel_button)
                
                layout.addLayout(buttons_layout)
            
            def get_notes(self):
                """Get the updated notes"""
                return self.notes_edit.toPlainText()
        
        # Show dialog
        dialog = VisitDetailsDialog(patient_id, patient_name, active_visit, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Update visit notes
            new_notes = dialog.get_notes()
            success, message = self.patient_manager.update_visit_notes(patient_id, new_notes)
            
            if success:
                QMessageBox.information(self, "Success", "Visit notes updated successfully.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to update notes: {message}")
            
            # Refresh view
            self.load_active_visits()
        elif result == 42:  # Custom result code for end visit
            # End visit - show end visit dialog
            self._end_visit(patient_id, patient_name)
    
    def _end_visit_clicked(self):
        """Handle end visit button click"""
        # Get the button that was clicked
        button = self.sender()
        if not button:
            return
        
        # Get patient ID from button property
        patient_id = button.property("patient_id")
        if not patient_id:
            return
        
        # Get patient name
        for row in range(self.visits_table.rowCount()):
            if self.visits_table.item(row, 0).text() == patient_id:
                patient_name = self.visits_table.item(row, 1).text()
                self._end_visit(patient_id, patient_name)
                return
    
    def _end_visit(self, patient_id, patient_name):
        """End a visit"""
        # Get active visit
        active_visit = self.patient_manager.get_active_visit(patient_id)
        
        if not active_visit:
            QMessageBox.warning(self, "Error", f"No active visit found for patient {patient_name}.")
            return
        
        class EndVisitDialog(QDialog):
            def __init__(self, patient_id, patient_name, active_visit, parent=None):
                super().__init__(parent)
                
                self.patient_id = patient_id
                self.patient_name = patient_name
                self.active_visit = active_visit
                
                # Set dialog properties
                self.setWindowTitle("End Visit")
                self.setMinimumSize(500, 400)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                """Set up the dialog UI"""
                layout = QVBoxLayout(self)
                
                # Patient info
                info_layout = QHBoxLayout()
                info_layout.addWidget(QLabel(f"Patient: {self.patient_name}"))
                info_layout.addWidget(QLabel(f"ID: {self.patient_id}"))
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
        
        # Show dialog
        dialog = EndVisitDialog(patient_id, patient_name, active_visit, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get visit notes
            visit_notes = dialog.get_visit_notes()
            
            # End visit
            success, message = self.patient_manager.end_visit(patient_id, visit_notes)
            
            if success:
                # Refresh table
                self.load_active_visits()
                
                # Show success message
                QMessageBox.information(self, "Success", f"Visit ended for patient {patient_name}.")
            else:
                # Show error message
                QMessageBox.warning(self, "Error", f"Failed to end visit: {message}")
    
    def _show_context_menu(self, position):
        """Show context menu for visits table"""
        # Check if a row is selected
        indexes = self.visits_table.selectedIndexes()
        if not indexes:
            return
        
        # Get row and patient ID
        row = indexes[0].row()
        patient_id = self.visits_table.item(row, 0).text()
        patient_name = self.visits_table.item(row, 1).text()
        
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        view_action = QAction("View Visit Details", self)
        view_action.triggered.connect(lambda: self._view_visit(row, 0))
        menu.addAction(view_action)
        
        # End visit action
        end_visit_action = QAction("End Visit", self)
        end_visit_action.triggered.connect(lambda: self._end_visit(patient_id, patient_name))
        menu.addAction(end_visit_action)
        
        # Show the menu
        menu.exec_(self.visits_table.viewport().mapToGlobal(position))
    
    def refresh(self):
        """Refresh the view"""
        self.load_active_visits()