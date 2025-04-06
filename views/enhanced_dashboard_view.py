# views/enhanced_dashboard_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QSizePolicy, QSpacerItem, QMainWindow, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer, QDate, QDateTime, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QIcon, QPixmap

import datetime
import os
import platform

from models.patient_manager import PatientManager
from models.appointment_manager import AppointmentManager

class AlertWidget(QFrame):
    """Widget for displaying alerts and notifications"""
    
    def __init__(self, title, message, alert_type="info", parent=None):
        super().__init__(parent)
        
        # Set frame properties based on alert type
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Set color based on alert type
        if alert_type == "warning":
            bg_color = "#FFF3CD"
            border_color = "#FFEEBA"
            icon = "warning.png"
        elif alert_type == "danger":
            bg_color = "#F8D7DA"
            border_color = "#F5C6CB"
            icon = "error.png"
        elif alert_type == "success":
            bg_color = "#D4EDDA"
            border_color = "#C3E6CB"
            icon = "success.png"
        else:  # info
            bg_color = "#D1ECF1"
            border_color = "#BEE5EB"
            icon = "info.png"
        
        # Apply stylesheet
        self.setStyleSheet(f"""
            AlertWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0px;
            }}
        """)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Try to load icon
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "assets", "icons", icon)
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path)
            icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("!")
        
        icon_label.setFixedSize(24, 24)
        layout.addWidget(icon_label)
        
        # Text content
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)
        
        layout.addLayout(text_layout, 1)  # 1 = stretch factor
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #555555;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

class StatsCard(QFrame):
    """Enhanced widget for displaying a statistic with title, value and trend indicator"""
    
    clicked = Signal()  # Signal when the card is clicked
    
    def __init__(self, title, value, previous_value=None, icon_path=None, color="#4a86e8"):
        super().__init__()
        
        self.color = color
        self.value = value
        self.previous_value = previous_value
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet(f"""
            StatsCard {{
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: palette(base);
                padding: 10px;
                margin: 5px;
            }}
            StatsCard:hover {{
                border-color: {color};
                background-color: palette(alternate-base);
                cursor: pointer;
            }}
        """)
        self.setMinimumHeight(120)
        self.setMinimumWidth(180)
        
        # Make the card clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Card header with title and icon
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
            header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Card value (main content)
        value_layout = QHBoxLayout()
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignLeft)
        value_label.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {color};")
        value_layout.addWidget(value_label)
        
        # Add trend indicator if previous value exists
        if previous_value is not None and isinstance(value, (int, float)) and isinstance(previous_value, (int, float)):
            trend_label = QLabel()
            
            # Calculate percentage change
            if previous_value != 0:
                change_pct = ((value - previous_value) / previous_value) * 100
                
                # Set icon and color based on trend
                if change_pct > 0:
                    trend_label.setText(f"↑ {abs(change_pct):.1f}%")
                    trend_label.setStyleSheet("color: green;")
                elif change_pct < 0:
                    trend_label.setText(f"↓ {abs(change_pct):.1f}%")
                    trend_label.setStyleSheet("color: red;")
                else:
                    trend_label.setText("•")
            else:
                # Handle division by zero
                if value > 0:
                    trend_label.setText("↑")
                    trend_label.setStyleSheet("color: green;")
                else:
                    trend_label.setText("•")
            
            trend_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            value_layout.addWidget(trend_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Store references
        self.title_label = title_label
        self.value_label = value_label
    
    def update_value(self, new_value, new_previous_value=None):
        """Update the displayed value and trend"""
        self.previous_value = self.value if new_previous_value is None else new_previous_value
        self.value = new_value
        
        # Update value label
        self.value_label.setText(str(new_value))
        
        # Force a repaint to update the widget
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press event to make the card clickable"""
        self.clicked.emit()
        super().mousePressEvent(event)

class EnhancedDashboardView(QWidget):
    """Enhanced dashboard view with more advanced features and analytics"""
    
    # Navigation signals
    navigate_to_patients = Signal()
    navigate_to_appointments = Signal()
    navigate_to_visits = Signal()
    navigate_to_reports = Signal()
    
    def __init__(self, config_manager, current_user=None, user_role=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        
        # Create managers
        self.patient_manager = PatientManager(config_manager)
        self.appointment_manager = AppointmentManager(config_manager)
        
        # Store previous metric values for trend calculation
        self.previous_metrics = {
            "active_visits": 0,
            "total_patients": 0,
            "todays_visits": 0,
            "todays_appointments": 0
        }
        
        # Setup UI
        self._setup_ui()
        
        # Load data
        self.refresh()
        
        # Setup refresh timer (every 60 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(60000)  # 60 seconds
    
    def _setup_ui(self):
        """Set up the dashboard UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Header with welcome and date/time
        header_layout = QVBoxLayout()
        
        # Welcome message
        user_display_name = self.config_manager.users.get(self.current_user, {}).get("name", self.current_user)
        welcome_label = QLabel(f"Welcome, {user_display_name}")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(welcome_label)
        
        # Current date and time display
        self.date_time_label = QLabel()
        self.date_time_label.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(self.date_time_label)
        
        # Update date time now
        self._update_datetime()
        
        main_layout.addLayout(header_layout)
        
        # Alerts section
        self.alerts_container = QVBoxLayout()
        main_layout.addLayout(self.alerts_container)
        
        # Create scrolling area for dashboard content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setObjectName("dashboardContent")
        content_widget.setStyleSheet("""
            QWidget#dashboardContent {
                background-color: transparent;
            }
        """)
        scroll_area.setWidget(content_widget)
        
        # Content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Key metrics section - 2x2 grid
        metrics_label = QLabel("Key Metrics")
        metrics_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(metrics_label)
        
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)
        
        # Create metric cards
        self.active_visits_card = StatsCard("Active Visits", "0", color="#4CAF50")
        self.active_visits_card.clicked.connect(self.navigate_to_visits.emit)
        metrics_grid.addWidget(self.active_visits_card, 0, 0)
        
        self.total_patients_card = StatsCard("Total Patients", "0", color="#2196F3")
        self.total_patients_card.clicked.connect(self.navigate_to_patients.emit)
        metrics_grid.addWidget(self.total_patients_card, 0, 1)
        
        self.todays_visits_card = StatsCard("Today's Visits", "0", color="#FF9800")
        self.todays_visits_card.clicked.connect(self.navigate_to_visits.emit)
        metrics_grid.addWidget(self.todays_visits_card, 1, 0)
        
        self.todays_appointments_card = StatsCard("Today's Appointments", "0", color="#9C27B0")
        self.todays_appointments_card.clicked.connect(self.navigate_to_appointments.emit)
        metrics_grid.addWidget(self.todays_appointments_card, 1, 1)
        
        content_layout.addLayout(metrics_grid)
        
        # Today's schedule section
        schedule_label = QLabel("Today's Schedule")
        schedule_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(schedule_label)
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)  # Time, Patient, Type, Status, Action
        self.schedule_table.setHorizontalHeaderLabels(["Time", "Patient", "Type", "Status", ""])
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.schedule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        self.schedule_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Patient
        self.schedule_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        self.schedule_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        self.schedule_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Action
        
        # Set fixed height for better layout
        self.schedule_table.setMinimumHeight(200)
        self.schedule_table.setMaximumHeight(300)
        
        content_layout.addWidget(self.schedule_table)
        
        # View all schedule button
        schedule_button_layout = QHBoxLayout()
        schedule_button_layout.addStretch()
        
        view_schedule_btn = QPushButton("View Full Schedule")
        view_schedule_btn.clicked.connect(self.navigate_to_appointments.emit)
        schedule_button_layout.addWidget(view_schedule_btn)
        
        content_layout.addLayout(schedule_button_layout)
        
        # Quick access section
        quick_access_label = QLabel("Quick Actions")
        quick_access_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(quick_access_label)
        
        # Quick access buttons
        quick_access_layout = QHBoxLayout()
        
        # Add patient button
        add_patient_btn = self._create_action_button(
            "Add Patient", 
            "person_add.png", 
            "Register a new patient in the system",
            self._add_patient
        )
        quick_access_layout.addWidget(add_patient_btn)
        
        # Add appointment button
        add_appointment_btn = self._create_action_button(
            "Schedule Appointment", 
            "calendar_add.png", 
            "Create a new appointment",
            self._add_appointment
        )
        quick_access_layout.addWidget(add_appointment_btn)
        
        # Start visit button
        start_visit_btn = self._create_action_button(
            "Start Visit", 
            "start_visit.png", 
            "Begin a new patient visit",
            self._start_visit
        )
        quick_access_layout.addWidget(start_visit_btn)
        
        # Create report button
        create_report_btn = self._create_action_button(
            "Generate Report", 
            "report.png", 
            "Create a patient or system report",
            self._generate_report
        )
        quick_access_layout.addWidget(create_report_btn)
        
        content_layout.addLayout(quick_access_layout)
        
        # Recent activity section
        activity_label = QLabel("Recent Activity")
        activity_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(activity_label)
        
        # Activity list
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)  # Time, Type, Description, User
        self.activity_table.setHorizontalHeaderLabels(["Time", "Type", "Description", "User"])
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.activity_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        self.activity_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        self.activity_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # User
        
        # Set fixed height for better layout
        self.activity_table.setMinimumHeight(150)
        self.activity_table.setMaximumHeight(250)
        
        content_layout.addWidget(self.activity_table)
        
        # Add scrolling area to main layout
        main_layout.addWidget(scroll_area, 1)  # 1 = stretch factor
        
        # Status bar
        status_bar_layout = QHBoxLayout()
        
        self.status_label = QLabel("")
        status_bar_layout.addWidget(self.status_label)
        
        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.refresh)
        status_bar_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(status_bar_layout)
    
    def _create_action_button(self, title, icon_name, tooltip, callback):
        """Create a styled action button for the quick access section"""
        button = QPushButton(title)
        button.setToolTip(tooltip)
        
        # Try to load icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "assets", "icons", icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))
        
        # Set button style
        button.setMinimumHeight(50)
        button.setStyleSheet("""
            QPushButton {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px 16px;
                background-color: palette(base);
                text-align: left;
            }
            QPushButton:hover {
                background-color: palette(alternate-base);
                border-color: #999999;
            }
        """)
        
        # Connect callback
        button.clicked.connect(callback)
        
        return button
    
    def _update_datetime(self):
        """Update the date and time display"""
        current_datetime = QDateTime.currentDateTime()
        formatted_date = current_datetime.toString("dddd, MMMM d, yyyy")
        formatted_time = current_datetime.toString("hh:mm AP")
        self.date_time_label.setText(f"{formatted_date} | {formatted_time}")
        
        # Schedule next update
        QTimer.singleShot(1000, self._update_datetime)
    
    def refresh(self):
        """Refresh all dashboard data"""
        # Save current metrics for trend calculation
        self._save_previous_metrics()
        
        # Clear any existing alerts
        self._clear_alerts()
        
        # Check for important alerts
        self._check_alerts()
        
        # Update key metrics
        self._update_metrics()
        
        # Update today's schedule
        self._update_schedule()
        
        # Update recent activity
        self._update_activity()
        
        # Update status
        self.status_label.setText(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def _save_previous_metrics(self):
        """Save current metric values for trend calculation"""
        try:
            # Extract numeric values
            self.previous_metrics["active_visits"] = int(self.active_visits_card.value)
            self.previous_metrics["total_patients"] = int(self.total_patients_card.value)
            self.previous_metrics["todays_visits"] = int(self.todays_visits_card.value)
            self.previous_metrics["todays_appointments"] = int(self.todays_appointments_card.value)
        except (ValueError, AttributeError):
            # If values can't be converted to int, just use 0
            pass
    
    def _clear_alerts(self):
        """Clear all existing alerts"""
        # Remove all widgets from the alerts container
        while self.alerts_container.count():
            item = self.alerts_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _check_alerts(self):
        """Check for important alerts to display"""
        # Example: Check for patients with appointments today but no active visit
        try:
            today = QDate.currentDate()
            today_appointments = self.appointment_manager.get_appointments_for_date(today)
            active_visits = self.patient_manager.get_all_active_visits()
            
            # Get patient IDs with appointments today
            appointment_patient_ids = set(appt.get("patient_id", "") for appt in today_appointments)
            
            # Get patient IDs with active visits
            active_visit_patient_ids = set(active_visits.keys())
            
            # Find patients with appointments but no active visit
            missing_visits = appointment_patient_ids - active_visit_patient_ids
            
            # Get appointments that should have started but haven't
            current_time = QDateTime.currentDateTime()
            missed_appointments = []
            
            for appt in today_appointments:
                patient_id = appt.get("patient_id", "")
                if patient_id in missing_visits:
                    # Check if appointment time has passed
                    appt_time_str = appt.get("datetime", "")
                    if appt_time_str:
                        try:
                            appt_time = datetime.datetime.fromisoformat(appt_time_str)
                            appt_qdt = QDateTime(
                                appt_time.year, appt_time.month, appt_time.day,
                                appt_time.hour, appt_time.minute
                            )
                            
                            # If appointment was more than 15 minutes ago
                            if appt_qdt.addSecs(15 * 60) < current_time:
                                missed_appointments.append(appt)
                        except:
                            # Skip if datetime parsing fails
                            pass
            
            # Create alert for missed appointments
            if missed_appointments:
                if len(missed_appointments) == 1:
                    # Get patient name
                    patient_id = missed_appointments[0].get("patient_id", "")
                    patient_data = self.patient_manager.get_patient(patient_id)
                    patient_name = patient_data.get("name", "Unknown") if patient_data else "Unknown"
                    
                    # Create alert
                    alert = AlertWidget(
                        "Missed Appointment",
                        f"Patient {patient_name} had an appointment but no visit has been started.",
                        "warning"
                    )
                else:
                    # Create alert for multiple missed appointments
                    alert = AlertWidget(
                        "Missed Appointments",
                        f"{len(missed_appointments)} patients had appointments but no visits have been started.",
                        "warning"
                    )
                
                self.alerts_container.addWidget(alert)
        
        except Exception as e:
            # Log the error but don't disrupt the dashboard
            self.config_manager.logger.error(f"Error checking alerts: {str(e)}")
    
    def _update_metrics(self):
        """Update the metrics cards with current data"""
        try:
            # Get all active visits
            active_visits = self.patient_manager.get_all_active_visits()
            self.active_visits_card.update_value(
                len(active_visits),
                self.previous_metrics["active_visits"]
            )
            
            # Get total patients
            patients = self.patient_manager.get_all_patients()
            self.total_patients_card.update_value(
                len(patients),
                self.previous_metrics["total_patients"]
            )
            
            # Count today's visits (completed and active)
            today = QDate.currentDate()
            today_visits_count = 0
            
            # Count completed visits that ended today
            for patient_data in patients.values():
                visit_history = patient_data.get("visit_history", [])
                
                for visit in visit_history:
                    end_time_str = visit.get("end_time", "")
                    if end_time_str:
                        try:
                            end_time = datetime.datetime.fromisoformat(end_time_str)
                            visit_date = QDate(end_time.year, end_time.month, end_time.day)
                            
                            if visit_date == today:
                                today_visits_count += 1
                        except:
                            # Skip if invalid date
                            pass
            
            # Add active visits that started today
            for patient_id, visit_info in active_visits.items():
                visit_data = visit_info.get("visit_data", {})
                start_time = visit_data.get("start_time")
                
                if start_time:
                    if isinstance(start_time, str):
                        try:
                            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        except:
                            continue
                    
                    if isinstance(start_time, datetime.datetime):
                        visit_date = QDate(start_time.year, start_time.month, start_time.day)
                        
                        if visit_date == today:
                            today_visits_count += 1
            
            self.todays_visits_card.update_value(
                today_visits_count,
                self.previous_metrics["todays_visits"]
            )
            
            # Count today's appointments
            today_appointments = self.appointment_manager.get_appointments_for_date(today)
            self.todays_appointments_card.update_value(
                len(today_appointments),
                self.previous_metrics["todays_appointments"]
            )
        
        except Exception as e:
            # Log the error but don't disrupt the dashboard
            self.config_manager.logger.error(f"Error updating metrics: {str(e)}")
    
    def _update_schedule(self):
        """Update today's schedule table"""
        try:
            # Clear existing rows
            self.schedule_table.setRowCount(0)
            
            # Get today's appointments
            today = QDate.currentDate()
            appointments = self.appointment_manager.get_appointments_for_date(today)
            
            # Get all active visits
            active_visits = self.patient_manager.get_all_active_visits()
            active_patient_ids = set(active_visits.keys())
            
            # Sort appointments by time
            appointments.sort(key=lambda x: x.get("datetime", ""))
            
            # Add appointments to table
            current_time = QDateTime.currentDateTime()
            
            for row, appointment in enumerate(appointments):
                self.schedule_table.insertRow(row)
                
                # Time
                time_str = "Unknown"
                is_past = False
                
                if "datetime" in appointment:
                    try:
                        dt = datetime.datetime.fromisoformat(appointment["datetime"])
                        time_str = dt.strftime("%I:%M %p")
                        
                        # Check if appointment time has passed
                        appt_qdt = QDateTime(
                            dt.year, dt.month, dt.day,
                            dt.hour, dt.minute
                        )
                        is_past = appt_qdt < current_time
                    except:
                        pass
                
                time_item = QTableWidgetItem(time_str)
                self.schedule_table.setItem(row, 0, time_item)
                
                # Patient
                patient_id = appointment.get("patient_id", "")
                patient_data = self.patient_manager.get_patient(patient_id)
                patient_name = patient_data.get("name", "Unknown") if patient_data else "Unknown"
                
                patient_item = QTableWidgetItem(patient_name)
                self.schedule_table.setItem(row, 1, patient_item)
                
                # Type (Appointment)
                type_item = QTableWidgetItem("Appointment")
                self.schedule_table.setItem(row, 2, type_item)
                
                # Status
                status = "Scheduled"
                color = QColor(0, 0, 0)  # Default black
                
                if appointment.get("status") == "completed":
                    status = "Completed"
                    color = QColor(0, 128, 0)  # Green

                elif appointment.get("status") == "cancelled":
                    status = "Cancelled"
                    color = QColor(128, 0, 0)  # Red
                elif patient_id in active_patient_ids:
                    status = "In Progress"
                    color = QColor(0, 0, 128)  # Blue
                elif is_past:
                    status = "Missed"
                    color = QColor(255, 165, 0)  # Orange
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(color)
                self.schedule_table.setItem(row, 3, status_item)
                
                # Action button
                action_button = QPushButton("View")
                action_button.setProperty("appointment_id", appointment.get("id", ""))
                action_button.clicked.connect(self._view_appointment)
                self.schedule_table.setCellWidget(row, 4, action_button)
            
            # Add active visits that aren't from appointments
            for patient_id, visit_info in active_visits.items():
                # Skip visits that are already in the appointments list
                already_in_table = False
                for appointment in appointments:
                    if appointment.get("patient_id") == patient_id:
                        already_in_table = True
                        break
                
                if already_in_table:
                    continue
                
                # Add row for this visit
                row = self.schedule_table.rowCount()
                self.schedule_table.insertRow(row)
                
                visit_data = visit_info.get("visit_data", {})
                
                # Time
                start_time = visit_data.get("start_time")
                time_str = "Unknown"
                
                if start_time:
                    if isinstance(start_time, str):
                        try:
                            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                            time_str = start_time.strftime("%I:%M %p")
                        except:
                            pass
                    elif isinstance(start_time, datetime.datetime):
                        time_str = start_time.strftime("%I:%M %p")
                
                time_item = QTableWidgetItem(time_str)
                self.schedule_table.setItem(row, 0, time_item)
                
                # Patient
                patient_data = self.patient_manager.get_patient(patient_id)
                patient_name = patient_data.get("name", "Unknown") if patient_data else "Unknown"
                
                patient_item = QTableWidgetItem(patient_name)
                self.schedule_table.setItem(row, 1, patient_item)
                
                # Type (Visit)
                type_item = QTableWidgetItem("Visit")
                self.schedule_table.setItem(row, 2, type_item)
                
                # Status
                status_item = QTableWidgetItem("In Progress")
                status_item.setForeground(QColor(0, 0, 128))  # Blue
                self.schedule_table.setItem(row, 3, status_item)
                
                # Action button
                action_button = QPushButton("View")
                action_button.setProperty("patient_id", patient_id)
                action_button.clicked.connect(self._view_patient_visit)
                self.schedule_table.setCellWidget(row, 4, action_button)
        
        except Exception as e:
            # Log the error but don't disrupt the dashboard
            self.config_manager.logger.error(f"Error updating schedule: {str(e)}")
    
    def _update_activity(self):
        """Update recent activity table with system events"""
        try:
            # Clear existing rows
            self.activity_table.setRowCount(0)
            
            # For now, we'll simulate recent activity based on available data
            # In a real implementation, you would have a proper activity log in the database
            
            activities = []
            
            # Check for recently updated patients
            patients = self.patient_manager.get_all_patients()
            for patient_id, patient_data in patients.items():
                # Get most recent update time
                last_updated = patient_data.get("last_updated")
                if not last_updated:
                    continue
                
                try:
                    update_time = datetime.datetime.fromisoformat(last_updated)
                    
                    # Only include if it's recent (last 24 hours)
                    if (datetime.datetime.now() - update_time).total_seconds() < 86400:  # 24 hours in seconds
                        activities.append({
                            "time": update_time,
                            "type": "Patient Update",
                            "description": f"Patient {patient_data.get('name', 'Unknown')} information updated",
                            "user": "Unknown"  # User info not tracked in current system
                        })
                except:
                    # Skip if date parsing fails
                    pass
            
            # Check for recently completed visits
            for patient_id, patient_data in patients.items():
                visit_history = patient_data.get("visit_history", [])
                
                for visit in visit_history:
                    end_time_str = visit.get("end_time", "")
                    if not end_time_str:
                        continue
                    
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time_str)
                        
                        # Only include if it's recent (last 24 hours)
                        if (datetime.datetime.now() - end_time).total_seconds() < 86400:  # 24 hours in seconds
                            activities.append({
                                "time": end_time,
                                "type": "Visit Completed",
                                "description": f"Visit for {patient_data.get('name', 'Unknown')} completed",
                                "user": visit.get("doctor", "Unknown")
                            })
                    except:
                        # Skip if date parsing fails
                        pass
            
            # Sort activities by time (most recent first)
            activities.sort(key=lambda x: x["time"], reverse=True)
            
            # Limit to most recent 10 activities
            activities = activities[:10]
            
            # Add to table
            for row, activity in enumerate(activities):
                self.activity_table.insertRow(row)
                
                # Format time
                time_str = activity["time"].strftime("%m/%d %I:%M %p")
                time_item = QTableWidgetItem(time_str)
                self.activity_table.setItem(row, 0, time_item)
                
                # Type
                type_item = QTableWidgetItem(activity["type"])
                self.activity_table.setItem(row, 1, type_item)
                
                # Description
                desc_item = QTableWidgetItem(activity["description"])
                self.activity_table.setItem(row, 2, desc_item)
                
                # User
                user_item = QTableWidgetItem(activity["user"])
                self.activity_table.setItem(row, 3, user_item)
        
        except Exception as e:
            # Log the error but don't disrupt the dashboard
            self.config_manager.logger.error(f"Error updating activity: {str(e)}")
    
    # Quick action handlers
    def _add_patient(self):
        """Handle add patient button click"""
        self.navigate_to_patients.emit()
        
        # The patients view will need to handle showing the add patient dialog
        # We can't directly open it from here since it's in another view
        
        # We could implement a specific signal for this:
        # self.show_add_patient_dialog.emit()
    
    def _add_appointment(self):
        """Handle add appointment button click"""
        self.navigate_to_appointments.emit()
        
        # Similar to above, the appointments view will need to handle showing the add dialog
    
    def _start_visit(self):
        """Handle start visit button click"""
        self.navigate_to_visits.emit()
    
    def _generate_report(self):
        """Handle generate report button click"""
        self.navigate_to_reports.emit()
    
    def _view_appointment(self):
        """Handle view appointment button click"""
        button = self.sender()
        if not button:
            return
            
        appointment_id = button.property("appointment_id")
        if not appointment_id:
            return
            
        # Navigate to appointments view
        self.navigate_to_appointments.emit()
        
        # We would need a way to tell the appointments view to focus on this appointment
        # Could be done with a specific signal:
        # self.focus_on_appointment.emit(appointment_id)
    
    def _view_patient_visit(self):
        """Handle view patient visit button click"""
        button = self.sender()
        if not button:
            return
            
        patient_id = button.property("patient_id")
        if not patient_id:
            return
            
        # Navigate to active visits view
        self.navigate_to_visits.emit()
        
        # We would need a way to tell the visits view to focus on this patient
        # Could be done with a specific signal:
        # self.focus_on_patient_visit.emit(patient_id)