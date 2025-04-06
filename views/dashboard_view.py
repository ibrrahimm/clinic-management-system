# views/dashboard_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, QTimer, QDate, QDateTime, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QIcon

import datetime
import os

from models.patient_manager import PatientManager
from models.appointment_manager import AppointmentManager  # We'll create this next

class MetricCard(QFrame):
    """Widget for displaying a metric with title and value"""
    
    def __init__(self, title, value, icon_path=None, color="#4a86e8"):
        super().__init__()
        
        self.color = color
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet(f"""
            MetricCard {{
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: palette(base);
            }}
        """)
        self.setMinimumHeight(100)
        
        # Set layout
        layout = QVBoxLayout(self)
        
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
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        # Store references
        self.title_label = title_label
        self.value_label = value_label
    
    def update_value(self, new_value):
        """Update the displayed value"""
        self.value_label.setText(str(new_value))


class AppointmentWidget(QFrame):
    """Widget for displaying upcoming appointments"""
    
    view_clicked = Signal(str)  # Signal to view appointment details
    
    def __init__(self, appointment_data):
        super().__init__()
        
        self.appointment_data = appointment_data
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            AppointmentWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
                margin: 2px 0px;
            }
            AppointmentWidget:hover {
                background-color: #f0f7ff;
            }
        """)
        
        # Set layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Time
        time_str = "Unknown"
        if "datetime" in appointment_data:
            dt = QDateTime.fromString(appointment_data["datetime"], Qt.ISODate)
            time_str = dt.toString("hh:mm AP")
            
        time_label = QLabel(time_str)
        time_label.setStyleSheet("font-weight: bold; min-width: 80px;")
        layout.addWidget(time_label)
        
        # Patient name
        patient_name = appointment_data.get("patient_name", "Unknown Patient")
        patient_label = QLabel(patient_name)
        layout.addWidget(patient_label)
        
        # Spacer
        layout.addStretch(1)
        
        # Doctor name
        doctor_name = appointment_data.get("doctor", "Unassigned")
        doctor_label = QLabel(f"Dr. {doctor_name}")
        layout.addWidget(doctor_label)
        
        # View button
        view_btn = QPushButton("View")
        view_btn.setMaximumWidth(60)
        view_btn.clicked.connect(self._on_view_clicked)
        layout.addWidget(view_btn)
    
    def _on_view_clicked(self):
        """Handle view button click"""
        self.view_clicked.emit(self.appointment_data.get("id", ""))


class RecentPatientWidget(QFrame):
    """Widget for displaying a recent patient"""
    
    view_clicked = Signal(str)  # Signal to view patient details
    
    def __init__(self, patient_data):
        super().__init__()
        
        self.patient_data = patient_data
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            RecentPatientWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
                margin: 2px 0px;
            }
            RecentPatientWidget:hover {
                background-color: #f0f7ff;
            }
        """)
        
        # Set layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Patient ID
        patient_id = patient_data.get("id", "Unknown")
        id_label = QLabel(patient_id)
        id_label.setStyleSheet("font-weight: bold; min-width: 80px;")
        layout.addWidget(id_label)
        
        # Patient name
        patient_name = patient_data.get("name", "Unknown Patient")
        name_label = QLabel(patient_name)
        layout.addWidget(name_label)
        
        # Spacer
        layout.addStretch(1)
        
        # Last activity (created or updated)
        activity_date = "Unknown"
        if "last_updated" in patient_data:
            try:
                dt = datetime.datetime.fromisoformat(patient_data["last_updated"])
                activity_date = dt.strftime("%Y-%m-%d")
            except:
                pass
        elif "created_on" in patient_data:
            try:
                dt = datetime.datetime.fromisoformat(patient_data["created_on"])
                activity_date = dt.strftime("%Y-%m-%d")
            except:
                pass
            
        date_label = QLabel(activity_date)
        layout.addWidget(date_label)
        
        # View button
        view_btn = QPushButton("View")
        view_btn.setMaximumWidth(60)
        view_btn.clicked.connect(self._on_view_clicked)
        layout.addWidget(view_btn)
    
    def _on_view_clicked(self):
        """Handle view button click"""
        self.view_clicked.emit(self.patient_data.get("id", ""))


class SimpleBarChart(QFrame):
    """Simple bar chart widget"""
    
    def __init__(self, title, data, color="#4a86e8"):
        super().__init__()
        
        self.title = title
        self.data = data  # List of (label, value) tuples
        self.color = color
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            SimpleBarChart {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: palette(base);
            }
        """)
    
    def paintEvent(self, event):
        """Paint the bar chart"""
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw title
        painter.setPen(QPen(self.palette().text().color()))  # Use text color from theme
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, self.title)
        
        # Calculate chart area
        chart_rect = self.rect().adjusted(40, 30, -10, -30)
        
        # Find maximum value for scaling
        max_value = max(value for _, value in self.data) if self.data else 1
        
        # Calculate bar width and spacing
        bar_count = len(self.data)
        if bar_count == 0:
            return
            
        bar_width = chart_rect.width() / (bar_count * 1.5)
        spacing = bar_width / 2
        
        # Draw bars
        painter.setPen(QPen(QColor(self.color)))
        painter.setBrush(QColor(self.color))
        
        # Draw axes
        painter.setPen(QPen(self.palette().text().color()))  # Use text color from theme
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())  # X-axis
        painter.drawLine(chart_rect.left(), chart_rect.top(), chart_rect.left(), chart_rect.bottom())  # Y-axis
        
        for i, (label, value) in enumerate(self.data):
            # Calculate bar position and height
            bar_height = (value / max_value) * chart_rect.height() if max_value > 0 else 0
            bar_left = chart_rect.left() + i * (bar_width + spacing)
            bar_top = chart_rect.bottom() - bar_height
            
            # Draw bar
            painter.setPen(QPen(QColor(self.color)))
            painter.setBrush(QColor(self.color))
            painter.drawRect(int(bar_left), int(bar_top), int(bar_width), int(bar_height))
            
            # Draw label
            painter.setPen(QPen(self.palette().text().color()))  # Use text color from theme
            painter.save()
            painter.translate(bar_left + bar_width/2, chart_rect.bottom() + 5)
            painter.rotate(-45)
            painter.drawText(0, 0, label)
            painter.restore()
            
            # Draw value on top of bar
            if bar_height > 20:  # Only if bar is tall enough
                painter.drawText(
                    int(bar_left), 
                    int(bar_top - 5), 
                    int(bar_width), 
                    20, 
                    Qt.AlignCenter, 
                    str(value)
                )


class DashboardView(QWidget):
    """Main dashboard view showing clinic summary and metrics"""
    
    view_patient = Signal(str)  # Signal to view patient details
    view_appointment = Signal(str)  # Signal to view appointment details
    
    def __init__(self, config_manager, current_user=None, user_role=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        
        # Create managers
        self.patient_manager = PatientManager(config_manager)
        self.appointment_manager = AppointmentManager(config_manager)
        
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
        main_layout.setSpacing(10)
        
        # Header with title
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Current date and time display
        date_time_label = QLabel()
        date_time_label.setAlignment(Qt.AlignCenter)
        date_time_label.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(date_time_label)
        self.date_time_label = date_time_label
        
        # Update date time now
        self._update_datetime()
        
        # Create scrolling area for dashboard content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setObjectName("dashboardContent")  # Add ID for styling
        content_widget.setStyleSheet("""
            QWidget#dashboardContent {
                background-color: transparent;
            }
        """)
        scroll_area.setWidget(content_widget)
        
        # Content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Metrics section
        metrics_layout = QHBoxLayout()
        
        # These cards will be created dynamically when data is loaded
        self.active_visits_card = MetricCard("Active Visits", "0", color="#4CAF50")
        metrics_layout.addWidget(self.active_visits_card)
        
        self.total_patients_card = MetricCard("Total Patients", "0", color="#2196F3")
        metrics_layout.addWidget(self.total_patients_card)
        
        self.todays_visits_card = MetricCard("Today's Visits", "0", color="#FF9800")
        metrics_layout.addWidget(self.todays_visits_card)
        
        self.todays_appointments_card = MetricCard("Today's Appointments", "0", color="#9C27B0")
        metrics_layout.addWidget(self.todays_appointments_card)
        
        content_layout.addLayout(metrics_layout)
        
        # Two column layout for appointments and recent patients
        columns_layout = QHBoxLayout()
        
        # Left column - Upcoming appointments
        appointments_layout = QVBoxLayout()
        appointments_label = QLabel("Upcoming Appointments")
        appointments_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        appointments_layout.addWidget(appointments_label)
        
        # Appointments container
        self.appointments_container = QVBoxLayout()
        appointments_layout.addLayout(self.appointments_container)
        
        # View all appointments button
        view_all_appts_btn = QPushButton("View All Appointments")
        view_all_appts_btn.clicked.connect(self._view_all_appointments)
        appointments_layout.addWidget(view_all_appts_btn)
        
        columns_layout.addLayout(appointments_layout)
        
        # Right column - Recent patients
        recent_layout = QVBoxLayout()
        recent_label = QLabel("Recent Patients")
        recent_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        recent_layout.addWidget(recent_label)
        
        # Recent patients container
        self.recent_container = QVBoxLayout()
        recent_layout.addLayout(self.recent_container)
        
        # View all patients button
        view_all_patients_btn = QPushButton("View All Patients")
        view_all_patients_btn.clicked.connect(self._view_all_patients)
        recent_layout.addWidget(view_all_patients_btn)
        
        columns_layout.addLayout(recent_layout)
        
        content_layout.addLayout(columns_layout)
        
        # Chart section - weekly visits
        self.weekly_chart = SimpleBarChart("Visits This Week", [])
        content_layout.addWidget(self.weekly_chart)
        
        # Add scrolling area to main layout
        main_layout.addWidget(scroll_area)

    
    def _update_datetime(self):
        """Update the date and time display"""
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("dddd, MMMM d, yyyy - hh:mm AP")
        self.date_time_label.setText(formatted_datetime)
        
        # Schedule next update
        QTimer.singleShot(1000, self._update_datetime)
    
    def refresh(self):
        """Refresh all dashboard data"""
        # Update metrics
        self._update_metrics()
        
        # Update appointments list
        self._update_appointments()
        
        # Update recent patients
        self._update_recent_patients()
        
        # Update chart data
        self._update_charts()
    
    def _update_metrics(self):
        """Update the metrics cards with current data"""
        # Get all active visits
        active_visits = self.patient_manager.get_all_active_visits()
        self.active_visits_card.update_value(len(active_visits))
        
        # Get total patients
        patients = self.patient_manager.get_all_patients()
        self.total_patients_card.update_value(len(patients))
        
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
        
        self.todays_visits_card.update_value(today_visits_count)
        
        # Count today's appointments
        today_appointments = self.appointment_manager.get_appointments_for_date(today)
        self.todays_appointments_card.update_value(len(today_appointments))
    
    def _update_appointments(self):
        """Update the upcoming appointments list"""
        # Clear existing widgets
        while self.appointments_container.count():
            item = self.appointments_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get upcoming appointments (next 7 days)
        today = QDate.currentDate()
        end_date = today.addDays(7)
        
        upcoming_appointments = self.appointment_manager.get_appointments_in_range(today, end_date)
        
        # Sort by date/time
        upcoming_appointments.sort(key=lambda x: x.get("datetime", ""))
        
        # Limit to 5 for display
        for appointment in upcoming_appointments[:5]:
            widget = AppointmentWidget(appointment)
            widget.view_clicked.connect(self.view_appointment.emit)
            self.appointments_container.addWidget(widget)
        
        # Add spacer if less than 5 appointments
        if len(upcoming_appointments) < 5:
            self.appointments_container.addStretch()
        
        # If no appointments, add a message
        if not upcoming_appointments:
            no_appts_label = QLabel("No upcoming appointments")
            no_appts_label.setAlignment(Qt.AlignCenter)
            no_appts_label.setStyleSheet("color: gray; padding: 20px;")
            self.appointments_container.addWidget(no_appts_label)
    
    def _update_recent_patients(self):
        """Update the recent patients list"""
        # Clear existing widgets
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get all patients
        patients = self.patient_manager.get_all_patients()
        
        # Convert to list and sort by creation/update date
        patient_list = []
        for patient_id, patient_data in patients.items():
            # Add ID to data
            patient_data_with_id = patient_data.copy()
            patient_data_with_id["id"] = patient_id
            patient_list.append(patient_data_with_id)
        
        # Function to get sort key (most recent updated or created date)
        def get_sort_key(patient):
            last_updated = patient.get("last_updated", "")
            created_on = patient.get("created_on", "")
            
            if last_updated:
                return last_updated
            return created_on
        
        # Sort by date (most recent first)
        patient_list.sort(key=get_sort_key, reverse=True)
        
        # Show top 5
        for patient in patient_list[:5]:
            widget = RecentPatientWidget(patient)
            widget.view_clicked.connect(self.view_patient.emit)
            self.recent_container.addWidget(widget)
        
        # Add spacer if less than 5 patients
        if len(patient_list) < 5:
            self.recent_container.addStretch()
        
        # If no patients, add a message
        if not patient_list:
            no_patients_label = QLabel("No patients in system")
            no_patients_label.setAlignment(Qt.AlignCenter)
            no_patients_label.setStyleSheet("color: gray; padding: 20px;")
            self.recent_container.addWidget(no_patients_label)
    
    def _update_charts(self):
        """Update the charts with current data"""
        # Get data for weekly visits chart
        today = QDate.currentDate()
        start_of_week = today.addDays(-today.dayOfWeek() + 1)  # Start from Monday
        
        # Create day labels for the week
        day_labels = []
        day_counts = []
        
        for i in range(7):
            day = start_of_week.addDays(i)
            day_labels.append(day.toString("ddd"))
            day_counts.append(0)  # Initialize counts to 0
        
        # Count visits for each day of the week
        patients = self.patient_manager.get_all_patients()
        
        # Count completed visits
        for patient_data in patients.values():
            visit_history = patient_data.get("visit_history", [])
            
            for visit in visit_history:
                end_time_str = visit.get("end_time", "")
                if end_time_str:
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time_str)
                        visit_date = QDate(end_time.year, end_time.month, end_time.day)
                        
                        # Check if visit is in current week
                        days_from_start = start_of_week.daysTo(visit_date)
                        if 0 <= days_from_start < 7:
                            day_counts[days_from_start] += 1
                    except:
                        # Skip if invalid date
                        pass
        
        # Count active visits
        active_visits = self.patient_manager.get_all_active_visits()
        
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
                    
                    # Check if visit is in current week
                    days_from_start = start_of_week.daysTo(visit_date)
                    if 0 <= days_from_start < 7:
                        day_counts[days_from_start] += 1
        
        # Update chart data
        chart_data = list(zip(day_labels, day_counts))
        
        # Force chart to redraw with new data
        self.weekly_chart.data = chart_data
        self.weekly_chart.update()
        
    def _view_all_appointments(self):
        """Switch to the Appointments tab"""
        # Find the main window (parent of parent)
        main_window = self.parent()
        while main_window and not isinstance(main_window, QMainWindow):
            main_window = main_window.parent()
        
        if main_window:
            # Find the appointments tab and switch to it
            tab_widget = main_window.findChild(QTabWidget)
            if tab_widget:
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Appointments":
                        tab_widget.setCurrentIndex(i)
                        break

    def _view_all_patients(self):
        """Switch to the Patients tab"""
        # Find the main window (parent of parent)
        main_window = self.parent()
        while main_window and not isinstance(main_window, QMainWindow):
            main_window = main_window.parent()
        
        if main_window:
            # Find the patients tab and switch to it
            tab_widget = main_window.findChild(QTabWidget)
            if tab_widget:
                for i in range(tab_widget.count()):
                    if tab_widget.tabText(i) == "Patients":
                        tab_widget.setCurrentIndex(i)
                        break