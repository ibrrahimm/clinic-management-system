# views/appointment_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QDialog, QFormLayout, QTextEdit,
                             QDateEdit, QTimeEdit, QComboBox, QMessageBox, QHeaderView,
                             QMenu, QCalendarWidget, QSplitter, QFrame)
from PySide6.QtCore import Qt, QDate, QTime, QDateTime, Signal
from PySide6.QtGui import QCursor
import datetime
import uuid

from models.patient_manager import PatientManager
from models.appointment_manager import AppointmentManager

class AppointmentDetailDialog(QDialog):
    """Dialog for creating or editing an appointment"""
    
    def __init__(self, config_manager, appointment_data=None, patient_id=None, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.appointment_data = appointment_data or {}
        self.patient_id = patient_id or self.appointment_data.get("patient_id")
        
        # Create patient manager to get patient names
        self.patient_manager = PatientManager(config_manager)
        
        # Set dialog properties
        self.setWindowTitle("Appointment Details")
        self.setMinimumSize(500, 400)
        
        # Setup UI
        self._setup_ui()
        
        # Load appointment data if provided
        if appointment_data:
            self._load_appointment_data()
    
    def _setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Patient selection
        self.patient_combo = QComboBox()
        self._populate_patient_combo()
        form_layout.addRow("Patient:", self.patient_combo)
        
        # Date selection
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)
        
        # Time selection
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))  # Default to 9:00 AM
        form_layout.addRow("Time:", self.time_edit)
        
        # Duration selection
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["15 minutes", "30 minutes", "45 minutes", "60 minutes"])
        self.duration_combo.setCurrentIndex(1)  # Default to 30 minutes
        form_layout.addRow("Duration:", self.duration_combo)
        
        # Doctor selection
        self.doctor_combo = QComboBox()
        doctors = self.config_manager.config.get("doctors", [])
        self.doctor_combo.addItems(doctors)
        form_layout.addRow("Doctor:", self.doctor_combo)
        
        # Purpose/Reason
        self.reason_combo = QComboBox()
        self.reason_combo.setEditable(True)
        reasons = self.config_manager.config.get("visit_reasons", [])
        self.reason_combo.addItems(reasons)
        form_layout.addRow("Reason:", self.reason_combo)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter any additional notes about the appointment")
        form_layout.addRow("Notes:", self.notes_edit)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _populate_patient_combo(self):
        """Populate the patient selection combo box"""
        self.patient_combo.clear()
        
        # Get all patients
        patients = self.patient_manager.get_all_patients()
        
        # Add to combo box
        for patient_id, patient_data in patients.items():
            patient_name = patient_data.get("name", "Unknown")
            display_text = f"{patient_name} ({patient_id})"
            
            self.patient_combo.addItem(display_text, patient_id)
        
        # Set current patient if provided
        if self.patient_id:
            for i in range(self.patient_combo.count()):
                if self.patient_combo.itemData(i) == self.patient_id:
                    self.patient_combo.setCurrentIndex(i)
                    break
    
    def _load_appointment_data(self):
        """Load appointment data into form fields"""
        # Patient is already set in _populate_patient_combo
        
        # Date and time
        datetime_str = self.appointment_data.get("datetime", "")
        if datetime_str:
            try:
                dt = datetime.datetime.fromisoformat(datetime_str)
                self.date_edit.setDate(QDate(dt.year, dt.month, dt.day))
                self.time_edit.setTime(QTime(dt.hour, dt.minute))
            except:
                pass
        
        # Duration
        duration = self.appointment_data.get("duration", 30)
        duration_index = 1  # Default to 30 minutes
        
        if duration == 15:
            duration_index = 0
        elif duration == 45:
            duration_index = 2
        elif duration == 60:
            duration_index = 3
            
        self.duration_combo.setCurrentIndex(duration_index)
        
        # Doctor
        doctor = self.appointment_data.get("doctor", "")
        if doctor:
            index = self.doctor_combo.findText(doctor)
            if index >= 0:
                self.doctor_combo.setCurrentIndex(index)
        
        # Reason
        reason = self.appointment_data.get("reason", "")
        if reason:
            index = self.reason_combo.findText(reason)
            if index >= 0:
                self.reason_combo.setCurrentIndex(index)
            else:
                self.reason_combo.setCurrentText(reason)
        
        # Notes
        self.notes_edit.setText(self.appointment_data.get("notes", ""))
    
    def get_appointment_data(self):
        """Get appointment data from form fields"""
        # Get selected patient ID
        patient_id = self.patient_combo.currentData()
        
        if not patient_id:
            QMessageBox.warning(self, "Input Error", "Please select a patient.")
            return None
        
        # Get date and time
        date = self.date_edit.date()
        time = self.time_edit.time()
        
        # Combine into datetime string
        dt = datetime.datetime(
            date.year(), date.month(), date.day(),
            time.hour(), time.minute()
        )
        datetime_str = dt.isoformat()
        
        # Get duration (extract number from text)
        duration_text = self.duration_combo.currentText()
        duration = 30  # Default
        
        if "15" in duration_text:
            duration = 15
        elif "45" in duration_text:
            duration = 45
        elif "60" in duration_text:
            duration = 60
        
        # Get doctor
        doctor = self.doctor_combo.currentText()
        
        if not doctor:
            QMessageBox.warning(self, "Input Error", "Please select a doctor.")
            return None
        
        # Get reason
        reason = self.reason_combo.currentText()
        
        # Create appointment data dictionary
        appointment_data = {
            "patient_id": patient_id,
            "datetime": datetime_str,
            "duration": duration,
            "doctor": doctor,
            "reason": reason,
            "notes": self.notes_edit.toPlainText(),
            "status": "scheduled"
        }
        
        # If editing, preserve the ID
        if "id" in self.appointment_data:
            appointment_data["id"] = self.appointment_data["id"]
        
        return appointment_data


class DayViewWidget(QFrame):
    """Widget for displaying appointments for a specific day"""
    
    appointment_selected = Signal(str)  # Signal when appointment is selected
    
    def __init__(self, config_manager, date=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.appointment_manager = AppointmentManager(config_manager)
        self.patient_manager = PatientManager(config_manager)
        
        self.current_date = date or QDate.currentDate()
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Set up UI
        self._setup_ui()
        
        # Load appointments
        self.refresh()
    
    def _setup_ui(self):
        """Set up the day view UI"""
        layout = QVBoxLayout(self)
        
        # Header with date
        header_layout = QHBoxLayout()
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self._update_date_label()
        header_layout.addWidget(self.date_label)
        
        # Add navigation buttons
        prev_day_btn = QPushButton("Previous Day")
        prev_day_btn.clicked.connect(self._go_to_previous_day)
        header_layout.addWidget(prev_day_btn)
        
        next_day_btn = QPushButton("Next Day")
        next_day_btn.clicked.connect(self._go_to_next_day)
        header_layout.addWidget(next_day_btn)
        
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self._go_to_today)
        header_layout.addWidget(today_btn)
        
        layout.addLayout(header_layout)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(6)  # Time, Duration, Patient, Reason, Doctor, Status
        self.appointments_table.setHorizontalHeaderLabels(["Time", "Duration", "Patient", "Reason", "Doctor", "Status"])
        self.appointments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.appointments_table.setSelectionMode(QTableWidget.SingleSelection)
        self.appointments_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.appointments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        self.appointments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Duration
        self.appointments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Patient
        self.appointments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Reason
        self.appointments_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Doctor
        self.appointments_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        
        # Connect double-click signal
        self.appointments_table.cellDoubleClicked.connect(self._on_appointment_double_clicked)
        
        layout.addWidget(self.appointments_table)
    
    def _update_date_label(self):
        """Update the date label with current date"""
        self.date_label.setText(self.current_date.toString("dddd, MMMM d, yyyy"))
    
    def _go_to_previous_day(self):
        """Navigate to previous day"""
        self.current_date = self.current_date.addDays(-1)
        self._update_date_label()
        self.refresh()
    
    def _go_to_next_day(self):
        """Navigate to next day"""
        self.current_date = self.current_date.addDays(1)
        self._update_date_label()
        self.refresh()
    
    def _go_to_today(self):
        """Navigate to today"""
        self.current_date = QDate.currentDate()
        self._update_date_label()
        self.refresh()
    
    def set_date(self, date):
        """Set the current date and refresh view"""
        self.current_date = date
        self._update_date_label()
        self.refresh()
    
    def refresh(self):
        """Refresh the appointments display"""
        self.appointments_table.setRowCount(0)
        
        # Get appointments for the current date
        appointments = self.appointment_manager.get_appointments_for_date(self.current_date)
        
        # Add to table
        for row, appointment in enumerate(appointments):
            self.appointments_table.insertRow(row)
            
            # Time
            time_str = "Unknown"
            if "datetime" in appointment:
                try:
                    dt = datetime.datetime.fromisoformat(appointment["datetime"])
                    time_str = dt.strftime("%I:%M %p")
                except:
                    pass
                
            time_item = QTableWidgetItem(time_str)
            self.appointments_table.setItem(row, 0, time_item)
            
            # Duration
            duration = appointment.get("duration", 30)
            duration_item = QTableWidgetItem(f"{duration} min")
            self.appointments_table.setItem(row, 1, duration_item)
            
            # Patient
            patient_id = appointment.get("patient_id", "")
            patient_data = self.patient_manager.get_patient(patient_id)
            patient_name = patient_data.get("name", "Unknown") if patient_data else "Unknown"
            
            patient_item = QTableWidgetItem(f"{patient_name} ({patient_id})")
            self.appointments_table.setItem(row, 2, patient_item)
            
            # Reason
            reason_item = QTableWidgetItem(appointment.get("reason", ""))
            self.appointments_table.setItem(row, 3, reason_item)
            
            # Doctor
            doctor_item = QTableWidgetItem(appointment.get("doctor", ""))
            self.appointments_table.setItem(row, 4, doctor_item)
            
            # Status
            status = appointment.get("status", "scheduled")
            status_item = QTableWidgetItem(status.capitalize())
            
            # Color-code status
            if status == "completed":
                status_item.setForeground(Qt.darkGreen)
            elif status == "cancelled":
                status_item.setForeground(Qt.red)
            elif status == "scheduled":
                status_item.setForeground(Qt.blue)
                
            self.appointments_table.setItem(row, 5, status_item)
            
            # Store appointment ID in first column for reference
            time_item.setData(Qt.UserRole, appointment.get("id", ""))
    
    def _on_appointment_double_clicked(self, row, column):
        """Handle double-click on appointment row"""
        appointment_id = self.appointments_table.item(row, 0).data(Qt.UserRole)
        if appointment_id:
            self.appointment_selected.emit(appointment_id)


class MonthViewWidget(QCalendarWidget):
    """Custom calendar widget for displaying month view with appointments"""
    
    date_selected = Signal(QDate)  # Signal when a date is selected
    
    def __init__(self, config_manager):
        super().__init__()
        
        self.config_manager = config_manager
        self.appointment_manager = AppointmentManager(config_manager)
        
        # Configure calendar appearance
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        
        # Connect signals
        self.clicked.connect(self.date_selected.emit)
        
        # Track appointments per day
        self.appointments_by_date = {}
        
        # Load appointments
        self.refresh()
    
    def refresh(self):
        """Refresh the calendar with current appointments"""
        # Clear existing data
        self.appointments_by_date = {}
        
        # Get current month and year
        current_date = self.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        # Create start and end dates for the visible month
        # Add padding for dates from previous/next months that are visible
        first_day = QDate(year, month, 1)
        days_in_month = first_day.daysInMonth()
        last_day = QDate(year, month, days_in_month)
        
        # Adjust to include visible days from previous month
        first_visible_day = first_day.addDays(-first_day.dayOfWeek() + 1)
        if first_visible_day > first_day:
            first_visible_day = first_visible_day.addDays(-7)
            
        # Adjust to include visible days from next month
        last_visible_day = last_day.addDays(7 - last_day.dayOfWeek())
        if last_visible_day < last_day:
            last_visible_day = last_visible_day.addDays(7)
        
        # Get appointments in the visible date range
        appointments = self.appointment_manager.get_appointments_in_range(
            first_visible_day, last_visible_day)
        
        # Group appointments by date
        for appointment in appointments:
            try:
                dt = datetime.datetime.fromisoformat(appointment.get("datetime", ""))
                date_key = QDate(dt.year, dt.month, dt.day)
                
                if date_key not in self.appointments_by_date:
                    self.appointments_by_date[date_key] = []
                    
                self.appointments_by_date[date_key].append(appointment)
            except:
                # Skip appointments with invalid dates
                continue
        
        # Update the calendar display
        self.updateCells()
    
    def paintCell(self, painter, rect, date):
        """Customize cell painting to show appointment indicators"""
        # Call the base implementation first
        super().paintCell(painter, rect, date)
        
        # Check if this date has appointments
        if date in self.appointments_by_date:
            appointments = self.appointments_by_date[date]
            
            # Draw appointment indicators
            painter.save()
            
            # Draw a colored dot for each appointment (up to 4)
            dot_size = 4
            spacing = 2
            total_width = min(len(appointments), 4) * (dot_size + spacing) - spacing
            
            x_start = rect.center().x() - total_width / 2
            y_pos = rect.bottom() - 8
            
            for i, appointment in enumerate(appointments[:4]):  # Maximum 4 dots
                status = appointment.get("status", "scheduled")
                
                if status == "completed":
                    painter.setPen(Qt.darkGreen)
                    painter.setBrush(Qt.darkGreen)
                elif status == "cancelled":
                    painter.setPen(Qt.red)
                    painter.setBrush(Qt.red)
                else:
                    painter.setPen(Qt.blue)
                    painter.setBrush(Qt.blue)
                
                x = x_start + i * (dot_size + spacing)
                painter.drawEllipse(int(x), int(y_pos), dot_size, dot_size)
            
            # If there are more than 4 appointments, add a "+"
            if len(appointments) > 4:
                painter.setPen(Qt.black)
                painter.drawText(
                    rect.right() - 12, 
                    rect.bottom() - 5, 
                    "+"
                )
            
            painter.restore()


class AppointmentView(QWidget):
    """Main appointment scheduling and management view"""
    
    def __init__(self, config_manager, current_user=None, user_role=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        
        # Create managers
        self.appointment_manager = AppointmentManager(config_manager)
        self.patient_manager = PatientManager(config_manager)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the appointments view UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title and actions
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Appointment Scheduling")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Search field
        search_label = QLabel("Search:")
        header_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search appointments...")
        self.search_edit.setMaximumWidth(250)
        self.search_edit.textChanged.connect(self._filter_appointments)
        header_layout.addWidget(self.search_edit)
        
        # Add spacer
        header_layout.addStretch(1)
        
        # Add appointment button
        add_btn = QPushButton("Add Appointment")
        add_btn.clicked.connect(self._add_appointment)
        header_layout.addWidget(add_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Split view for calendar and day view
        splitter = QSplitter(Qt.Horizontal)
        
        # Month calendar widget
        self.month_view = MonthViewWidget(self.config_manager)
        splitter.addWidget(self.month_view)
        
        # Day view widget
        self.day_view = DayViewWidget(self.config_manager)
        splitter.addWidget(self.day_view)
        
        # Connect signals
        self.month_view.date_selected.connect(self.day_view.set_date)
        self.day_view.appointment_selected.connect(self._view_appointment)
        
        main_layout.addWidget(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        # Status bar
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
    
    def _add_appointment(self):
        """Add a new appointment"""
        dialog = AppointmentDetailDialog(self.config_manager, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get appointment data
            appointment_data = dialog.get_appointment_data()
            
            if appointment_data:
                # Add appointment
                success, message = self.appointment_manager.add_appointment(appointment_data)
                
                if success:
                    self.status_label.setText("Appointment added successfully")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add appointment: {message}")
    
    def _view_appointment(self, appointment_id):
        """View and edit an appointment"""
        # Get appointment data
        appointment_data = self.appointment_manager.get_appointment(appointment_id)
        
        if not appointment_data:
            QMessageBox.warning(self, "Error", f"Appointment not found")
            return
        
        # Create a popup menu with options
        menu = QMenu(self)
        
        view_action = QAction("View/Edit Appointment", self)
        menu.addAction(view_action)
        
        status = appointment_data.get("status", "scheduled")
        
        if status == "scheduled":
            complete_action = QAction("Mark as Completed", self)
            menu.addAction(complete_action)
            
            cancel_action = QAction("Cancel Appointment", self)
            menu.addAction(cancel_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Appointment", self)
        menu.addAction(delete_action)
        
        # Get the global cursor position
        global_pos = QCursor.pos()
        
        # Show menu at cursor position
        action = menu.exec_(global_pos)
        
        if action == view_action:
            self._edit_appointment(appointment_id, appointment_data)
        elif action == complete_action if 'complete_action' in locals() else None:
            self._complete_appointment(appointment_id)
        elif action == cancel_action if 'cancel_action' in locals() else None:
            self._cancel_appointment(appointment_id)
        elif action == delete_action:
            self._delete_appointment(appointment_id)
    
    def _edit_appointment(self, appointment_id, appointment_data):
        """Edit an existing appointment"""
        # Create copy with ID included
        appointment_with_id = appointment_data.copy()
        appointment_with_id["id"] = appointment_id
        
        dialog = AppointmentDetailDialog(
            self.config_manager, 
            appointment_data=appointment_with_id, 
            parent=self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated appointment data
            updated_data = dialog.get_appointment_data()
            
            if updated_data:
                # Update appointment
                success, message = self.appointment_manager.update_appointment(
                    appointment_id, updated_data)
                
                if success:
                    self.status_label.setText("Appointment updated successfully")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update appointment: {message}")
    
    def _complete_appointment(self, appointment_id):
        """Mark an appointment as completed"""
        # Ask for notes
        notes, ok = QInputDialog.getMultiLineText(
            self, "Completion Notes", "Enter any notes about the appointment:")
        
        if ok:
            success, message = self.appointment_manager.mark_appointment_completed(
                appointment_id, notes)
            
            if success:
                self.status_label.setText("Appointment marked as completed")
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", f"Failed to update appointment: {message}")
    
    def _cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        # Ask for reason
        reason, ok = QInputDialog.getText(
            self, "Cancellation Reason", "Enter reason for cancellation:")
        
        if ok:
            success, message = self.appointment_manager.mark_appointment_cancelled(
                appointment_id, reason)
            
            if success:
                self.status_label.setText("Appointment cancelled")
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", f"Failed to cancel appointment: {message}")
    
    def _delete_appointment(self, appointment_id):
        """Delete an appointment"""
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this appointment? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.appointment_manager.delete_appointment(appointment_id)
            
            if success:
                self.status_label.setText("Appointment deleted")
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete appointment: {message}")
    
    def _filter_appointments(self):
        """Filter appointments based on search text (updated in month view)"""
        # This would require a custom implementation in MonthViewWidget
        # For now, we'll just refresh to show all appointments
        self.refresh()
        
        # Update status with search message
        search_text = self.search_edit.text()
        if search_text:
            self.status_label.setText(f"Searching for: {search_text}")
        else:
            self.status_label.setText("")
    
    def refresh(self):
        """Refresh the appointment views"""
        self.month_view.refresh()
        self.day_view.refresh()