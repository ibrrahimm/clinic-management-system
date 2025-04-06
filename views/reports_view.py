# views/reports_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTabWidget, QFormLayout, QDateEdit,
                              QComboBox, QCheckBox, QTextEdit, QFrame,
                              QScrollArea, QGroupBox, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QDate, Signal

import datetime
import os
from pathlib import Path

from models.patient_manager import PatientManager

class ReportsView(QWidget):
    """View for generating various clinic reports"""
    
    def __init__(self, config_manager, current_user=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_user = current_user or "admin"
        
        # Create patient manager
        self.patient_manager = PatientManager(config_manager)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the reports view UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Reports & Analytics")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Export button
        self.export_button = QPushButton("Export Report")
        self.export_button.setEnabled(False)  # Disable until report is generated
        self.export_button.clicked.connect(self._export_report)
        header_layout.addWidget(self.export_button)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._generate_report)
        header_layout.addWidget(refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Report controls section
        controls_group = QGroupBox("Report Options")
        controls_layout = QFormLayout(controls_group)
        
        # Report type
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Patient Summary", 
            "Visit Summary", 
            "Daily Visits", 
            "Weekly Visits", 
            "Monthly Visits", 
            "Custom Date Range"
        ])
        self.report_type_combo.currentTextChanged.connect(self._on_report_type_changed)
        controls_layout.addRow("Report Type:", self.report_type_combo)
        
        # Date range
        date_range_layout = QHBoxLayout()
        
        # From date
        from_date_layout = QVBoxLayout()
        from_date_label = QLabel("From:")
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addDays(-7))
        from_date_layout.addWidget(from_date_label)
        from_date_layout.addWidget(self.from_date_edit)
        date_range_layout.addLayout(from_date_layout)
        
        # To date
        to_date_layout = QVBoxLayout()
        to_date_label = QLabel("To:")
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        to_date_layout.addWidget(to_date_label)
        to_date_layout.addWidget(self.to_date_edit)
        date_range_layout.addLayout(to_date_layout)
        
        controls_layout.addRow("Date Range:", date_range_layout)
        
        # Include detailed records checkbox
        self.details_checkbox = QCheckBox("Include detailed records")
        controls_layout.addRow("Details:", self.details_checkbox)
        
        # Generate button
        generate_button = QPushButton("Generate Report")
        generate_button.clicked.connect(self._generate_report)
        controls_layout.addRow("", generate_button)
        
        main_layout.addWidget(controls_group)
        
        # Report display area
        report_group = QGroupBox("Generated Report")
        report_layout = QVBoxLayout(report_group)
        
        # Text area for report
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        report_layout.addWidget(self.report_text)
        
        main_layout.addWidget(report_group, 1)  # 1 = stretch factor
        
        # Set initial report type
        self._on_report_type_changed("Patient Summary")
    
    def _on_report_type_changed(self, report_type):
        """Handle report type change"""
        # Set appropriate date range based on report type
        today = QDate.currentDate()
        
        if report_type == "Patient Summary" or report_type == "Visit Summary":
            # Disable date controls - not used for these reports
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)
            
        elif report_type == "Daily Visits":
            # Set both dates to today
            self.from_date_edit.setDate(today)
            self.to_date_edit.setDate(today)
            
            # Disable date controls
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)
            
        elif report_type == "Weekly Visits":
            # Set date range to current week (starting Monday)
            start_of_week = today.addDays(-today.dayOfWeek() + 1)  # Monday
            self.from_date_edit.setDate(start_of_week)
            self.to_date_edit.setDate(today)
            
            # Disable date controls
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)
            
        elif report_type == "Monthly Visits":
            # Set date range to current month
            start_of_month = QDate(today.year(), today.month(), 1)
            self.from_date_edit.setDate(start_of_month)
            self.to_date_edit.setDate(today)
            
            # Disable date controls
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)
            
        else:  # Custom Date Range
            # Enable date controls
            self.from_date_edit.setEnabled(True)
            self.to_date_edit.setEnabled(True)
    
    def _generate_report(self):
        """Generate and display a report"""
        try:
            # Get report parameters
            report_type = self.report_type_combo.currentText()
            from_date = self.from_date_edit.date().toPython()
            to_date = self.to_date_edit.date().toPython()
            include_details = self.details_checkbox.isChecked()
            
            # Ensure "to" date is end of day
            to_date = datetime.datetime.combine(to_date, datetime.time(23, 59, 59))
            
            # Validate date range
            if from_date > to_date.date():
                QMessageBox.warning(self, "Invalid Date Range", 
                                    "Start date must be before end date.")
                return
            
            # Generate report based on type
            if report_type == "Patient Summary":
                report_text = self._generate_patient_summary(include_details)
            elif report_type == "Visit Summary":
                report_text = self._generate_visit_summary(include_details)
            elif report_type == "Daily Visits":
                report_text = self._generate_visits_report("daily", from_date, include_details)
            elif report_type == "Weekly Visits":
                report_text = self._generate_visits_report("weekly", from_date, include_details)
            elif report_type == "Monthly Visits":
                report_text = self._generate_visits_report("monthly", from_date, include_details)
            else:  # Custom Date Range
                report_text = self._generate_visits_report("custom", from_date, include_details, to_date)
            
            # Display report
            self.report_text.setText(report_text)
            
            # Enable export button
            self.export_button.setEnabled(True)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.config_manager.logger.error(f"Error generating report: {str(e)}\n{error_details}")
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def _generate_patient_summary(self, include_details):
        """Generate a summary report of patients"""
        # Get clinic information
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        
        # Get all patients
        patients = self.patient_manager.get_all_patients()
        
        # Report header
        report = f"{clinic_name} - Patient Summary\n"
        report += f"{'='*50}\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Generated by: {self.current_user}\n\n"
        
        # Summary statistics
        total_patients = len(patients)
        
        # Count patients by gender
        gender_counts = {"Male": 0, "Female": 0, "Other": 0}
        for patient_data in patients.values():
            gender = patient_data.get("gender", "")
            if gender in gender_counts:
                gender_counts[gender] += 1
        
        # Count patients by age groups
        age_groups = {
            "0-18": 0,
            "19-35": 0,
            "36-50": 0,
            "51-65": 0,
            "66+": 0
        }
        
        current_date = datetime.date.today()
        for patient_data in patients.values():
            dob_str = patient_data.get("dob", "")
            if dob_str:
                try:
                    dob_date = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
                    age = current_date.year - dob_date.year
                    
                    # Adjust if birthday hasn't occurred yet this year
                    if (current_date.month, current_date.day) < (dob_date.month, dob_date.day):
                        age -= 1
                    
                    # Add to appropriate age group
                    if age <= 18:
                        age_groups["0-18"] += 1
                    elif age <= 35:
                        age_groups["19-35"] += 1
                    elif age <= 50:
                        age_groups["36-50"] += 1
                    elif age <= 65:
                        age_groups["51-65"] += 1
                    else:
                        age_groups["66+"] += 1
                except:
                    # Skip if DOB is invalid
                    pass
        
        # Add summary statistics to report
        report += "SUMMARY\n"
        report += "-------\n"
        report += f"Total Patients: {total_patients}\n\n"
        
        report += "Patients by Gender:\n"
        for gender, count in gender_counts.items():
            percentage = (count / total_patients * 100) if total_patients > 0 else 0
            report += f"  {gender}: {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        report += "Patients by Age Group:\n"
        for age_group, count in age_groups.items():
            percentage = (count / total_patients * 100) if total_patients > 0 else 0
            report += f"  {age_group}: {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        # Include detailed patient list if requested
        if include_details:
            report += "PATIENT DETAILS\n"
            report += "===============\n\n"
            
            for patient_id, patient_data in patients.items():
                # Basic info
                report += f"ID: {patient_id}\n"
                report += f"Name: {patient_data.get('name', 'Unknown')}\n"
                report += f"Gender: {patient_data.get('gender', 'Unknown')}\n"
                report += f"DOB: {patient_data.get('dob', 'Unknown')}\n"
                report += f"Phone: {patient_data.get('phone', 'Unknown')}\n"
                report += f"Email: {patient_data.get('email', 'Unknown')}\n"
                
                # Medical history count
                medical_history = patient_data.get("medical_history", [])
                report += f"Medical Records: {len(medical_history)}\n"
                
                # Visit history count
                visit_history = patient_data.get("visit_history", [])
                report += f"Visit History: {len(visit_history)}\n"
                
                # Active visit status
                active_visits = self.patient_manager.get_all_active_visits()
                if patient_id in active_visits:
                    report += "Status: Currently in session\n"
                else:
                    report += "Status: Not in session\n"
                
                report += "-" * 40 + "\n\n"
        
        return report
    
    def _generate_visit_summary(self, include_details):
        """Generate a summary report of visits"""
        # Get clinic information
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        
        # Get all patients and their visit histories
        patients = self.patient_manager.get_all_patients()
        
        # Collect all visits
        all_visits = []
        for patient_id, patient_data in patients.items():
            visit_history = patient_data.get("visit_history", [])
            
            for visit in visit_history:
                # Add patient information to visit
                visit_copy = visit.copy()
                visit_copy["patient_id"] = patient_id
                visit_copy["patient_name"] = patient_data.get("name", "Unknown")
                
                all_visits.append(visit_copy)
        
        # Report header
        report = f"{clinic_name} - Visit Summary\n"
        report += f"{'='*50}\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Generated by: {self.current_user}\n\n"
        
        # Summary statistics
        total_visits = len(all_visits)
        
        if total_visits == 0:
            report += "No visit data available.\n"
            return report
        
        # Count visits by reason
        reason_counts = {}
        for visit in all_visits:
            reason = visit.get("reason", "Unknown")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Count visits by doctor
        doctor_counts = {}
        for visit in all_visits:
            doctor = visit.get("doctor", "Unknown")
            doctor_counts[doctor] = doctor_counts.get(doctor, 0) + 1
        
        # Count visits by month
        month_counts = {}
        for visit in all_visits:
            end_time_str = visit.get("end_time", "")
            if end_time_str:
                try:
                    end_time = datetime.datetime.fromisoformat(end_time_str)
                    month_key = end_time.strftime("%Y-%m")
                    month_counts[month_key] = month_counts.get(month_key, 0) + 1
                except:
                    # Skip if end_time is invalid
                    pass
        
        # Add summary statistics to report
        report += "SUMMARY\n"
        report += "-------\n"
        report += f"Total Visits: {total_visits}\n\n"
        
        report += "Visits by Reason:\n"
        for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_visits * 100)
            report += f"  {reason}: {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        report += "Visits by Doctor:\n"
        for doctor, count in sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_visits * 100)
            report += f"  {doctor}: {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        report += "Visits by Month:\n"
        for month, count in sorted(month_counts.items()):
            percentage = (count / total_visits * 100)
            try:
                # Format month nicely (YYYY-MM to Month YYYY)
                month_date = datetime.datetime.strptime(month, "%Y-%m")
                month_display = month_date.strftime("%B %Y")
            except:
                month_display = month
                
            report += f"  {month_display}: {count} ({percentage:.1f}%)\n"
        report += "\n"
        
        # Get active visits
        active_visits = self.patient_manager.get_all_active_visits()
        report += f"Active Visits: {len(active_visits)}\n\n"
        
        # Include detailed visit list if requested
        if include_details:
            report += "VISIT DETAILS\n"
            report += "=============\n\n"
            
            # Sort visits by end time (most recent first)
            sorted_visits = sorted(
                all_visits, 
                key=lambda x: x.get("end_time", ""), 
                reverse=True
            )
            
            for visit in sorted_visits:
                # Basic info
                patient_name = visit.get("patient_name", "Unknown")
                patient_id = visit.get("patient_id", "Unknown")
                report += f"Patient: {patient_name} (ID: {patient_id})\n"
                
                # Visit details
                end_time_str = visit.get("end_time", "Unknown")
                if end_time_str != "Unknown":
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time_str)
                        end_time_str = end_time.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                        
                report += f"Date: {end_time_str}\n"
                report += f"Doctor: {visit.get('doctor', 'Unknown')}\n"
                report += f"Reason: {visit.get('reason', 'Unknown')}\n"
                
                # Additional details
                if visit.get("diagnosis"):
                    report += f"Diagnosis: {visit['diagnosis']}\n"
                
                if visit.get("treatment"):
                    report += f"Treatment: {visit['treatment']}\n"
                
                if visit.get("follow_up"):
                    report += f"Follow-up: {visit['follow_up']}\n"
                
                if visit.get("notes"):
                    report += f"Notes: {visit['notes']}\n"
                
                report += "-" * 40 + "\n\n"
        
        return report
    
    def _generate_visits_report(self, report_period, from_date, include_details, to_date=None):
        """Generate a report of visits for a specific period"""
        # Get clinic information
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        
        # Set period-specific dates and title
        if report_period == "daily":
            report_title = f"Daily Visits Report - {from_date.strftime('%Y-%m-%d')}"
            to_date = datetime.datetime.combine(from_date, datetime.time(23, 59, 59))
        elif report_period == "weekly":
            # Find start of week (Monday)
            start_of_week = from_date - datetime.timedelta(days=from_date.weekday())
            from_date = start_of_week
            
            # Calculate end of week (Sunday)
            end_of_week = start_of_week + datetime.timedelta(days=6)
            to_date = datetime.datetime.combine(end_of_week, datetime.time(23, 59, 59))
            
            report_title = f"Weekly Visits Report - {from_date.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}"
        elif report_period == "monthly":
            # Find start of month
            start_of_month = from_date.replace(day=1)
            from_date = start_of_month
            
            # Calculate end of month
            if start_of_month.month == 12:
                next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
            else:
                next_month = start_of_month.replace(month=start_of_month.month + 1)
                
            end_of_month = next_month - datetime.timedelta(days=1)
            to_date = datetime.datetime.combine(end_of_month, datetime.time(23, 59, 59))
            
            report_title = f"Monthly Visits Report - {start_of_month.strftime('%B %Y')}"
        else:  # custom
            if not to_date:
                to_date = datetime.datetime.combine(from_date, datetime.time(23, 59, 59))
                
            report_title = f"Custom Visits Report - {from_date.strftime('%Y-%m-%d')} to {to_date.date().strftime('%Y-%m-%d')}"
        
        # Get all patients and their visit histories
        patients = self.patient_manager.get_all_patients()
        
        # Collect visits within the date range
        period_visits = []
        for patient_id, patient_data in patients.items():
            visit_history = patient_data.get("visit_history", [])
            
            for visit in visit_history:
                # Check if visit is within date range
                end_time_str = visit.get("end_time", "")
                if end_time_str:
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time_str)
                        
                        if from_date <= end_time.date() <= to_date.date():
                            # Visit is within range - add patient information
                            visit_copy = visit.copy()
                            visit_copy["patient_id"] = patient_id
                            visit_copy["patient_name"] = patient_data.get("name", "Unknown")
                            
                            period_visits.append(visit_copy)
                    except:
                        # Skip if end_time is invalid
                        pass
        
        # Get active visits that might not have an end_time yet
        active_visits = self.patient_manager.get_all_active_visits()
        active_visit_count = 0
        
        for patient_id, visit_info in active_visits.items():
            visit_data = visit_info.get("visit_data", {})
            start_time = visit_data.get("start_time")
            
            if start_time:
                if isinstance(start_time, str):
                    try:
                        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                
                # Check if active visit started within date range
                if from_date <= start_time.date() <= to_date.date():
                    active_visit_count += 1
        
        # Report header
        report = f"{clinic_name} - {report_title}\n"
        report += f"{'='*50}\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Generated by: {self.current_user}\n\n"
        
        # Summary statistics
        total_visits = len(period_visits)
        
        if total_visits == 0 and active_visit_count == 0:
            report += "No visits found in the selected period.\n"
            return report
        
        # Count visits by reason
        reason_counts = {}
        for visit in period_visits:
            reason = visit.get("reason", "Unknown")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Count visits by doctor
        doctor_counts = {}
        for visit in period_visits:
            doctor = visit.get("doctor", "Unknown")
            doctor_counts[doctor] = doctor_counts.get(doctor, 0) + 1
        
        # Count diagnoses
        diagnosis_counts = {}
        for visit in period_visits:
            diagnosis = visit.get("diagnosis", "")
            if diagnosis:
                diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
        
        # Add summary statistics to report
        report += "SUMMARY\n"
        report += "-------\n"
        report += f"Total Completed Visits: {total_visits}\n"
        report += f"Active Visits: {active_visit_count}\n"
        report += f"Total Visits: {total_visits + active_visit_count}\n\n"
        
        if total_visits > 0:
            report += "Visits by Reason:\n"
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_visits * 100)
                report += f"  {reason}: {count} ({percentage:.1f}%)\n"
            report += "\n"
            
            report += "Visits by Doctor:\n"
            for doctor, count in sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_visits * 100)
                report += f"  {doctor}: {count} ({percentage:.1f}%)\n"
            report += "\n"
            
            if diagnosis_counts:
                report += "Common Diagnoses:\n"
                for diagnosis, count in sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    percentage = (count / total_visits * 100)
                    report += f"  {diagnosis}: {count} ({percentage:.1f}%)\n"
                report += "\n"
        
        # Include detailed visit list if requested
        if include_details:
            report += "VISIT DETAILS\n"
            report += "=============\n\n"
            
            # Sort visits by end time (most recent first)
            sorted_visits = sorted(
                period_visits, 
                key=lambda x: x.get("end_time", ""), 
                reverse=True
            )
            
            for visit in sorted_visits:
                # Basic info
                patient_name = visit.get("patient_name", "Unknown")
                patient_id = visit.get("patient_id", "Unknown")
                report += f"Patient: {patient_name} (ID: {patient_id})\n"
                
                # Visit details
                end_time_str = visit.get("end_time", "Unknown")
                if end_time_str != "Unknown":
                    try:
                        end_time = datetime.datetime.fromisoformat(end_time_str)
                        end_time_str = end_time.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                        
                report += f"Date: {end_time_str}\n"
                report += f"Doctor: {visit.get('doctor', 'Unknown')}\n"
                report += f"Reason: {visit.get('reason', 'Unknown')}\n"
                
                # Additional details
                if visit.get("diagnosis"):
                    report += f"Diagnosis: {visit['diagnosis']}\n"
                
                if visit.get("treatment"):
                    report += f"Treatment: {visit['treatment']}\n"
                
                if visit.get("follow_up"):
                    report += f"Follow-up: {visit['follow_up']}\n"
                
                if visit.get("notes"):
                    report += f"Notes: {visit['notes']}\n"
                
                report += "-" * 40 + "\n\n"
            
            # Include active visits that started within date range
            if active_visit_count > 0:
                report += "ACTIVE VISITS\n"
                report += "============\n\n"
                
                for patient_id, visit_info in active_visits.items():
                    visit_data = visit_info.get("visit_data", {})
                    start_time = visit_data.get("start_time")
                    
                    if not start_time:
                        continue
                        
                    if isinstance(start_time, str):
                        try:
                            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            continue
                    
                    # Check if active visit started within date range
                    if from_date <= start_time.date() <= to_date.date():
                        patient_name = visit_info.get("patient_name", "Unknown")
                        
                        report += f"Patient: {patient_name} (ID: {patient_id})\n"
                        report += f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}\n"
                        report += f"Doctor: {visit_data.get('doctor', 'Unknown')}\n"
                        report += f"Reason: {visit_data.get('reason', 'Unknown')}\n"
                        
                        if visit_data.get("notes"):
                            report += f"Notes: {visit_data['notes']}\n"
                        
                        # Calculate duration
                        now = datetime.datetime.now()
                        duration = now - start_time
                        hours, remainder = divmod(duration.total_seconds(), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        
                        report += f"Duration: {int(hours)}:{int(minutes):02d}:{int(seconds):02d}\n"
                        report += f"Status: ACTIVE\n"
                        
                        report += "-" * 40 + "\n\n"
        
        return report
    
    def _export_report(self):
        """Export the current report to a file"""
        # Get report content
        report_content = self.report_text.toPlainText()
        if not report_content:
            QMessageBox.information(self, "Export", "No report to export.")
            return
        
        # Ask for filename and location
        report_type = self.report_type_combo.currentText().replace(" ", "_").lower()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"clinic_report_{report_type}_{timestamp}.txt"
        
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            default_filename,
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not export_path:
            return  # User cancelled
        
        # Save to file
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Report saved to {export_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                               f"Failed to export report: {str(e)}")
    
    def refresh(self):
        """Refresh the view - regenerate report if exists"""
        if self.report_text.toPlainText():
            self._generate_report()
    
    def set_current_user(self, username):
        """Set the current user for report generation"""
        self.current_user = username