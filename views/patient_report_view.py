# views/patient_report_view.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QCheckBox, QGroupBox, QMessageBox,
                              QFormLayout, QProgressDialog, QFileDialog)
from PySide6.QtCore import Qt, QTimer
import os
import subprocess
import platform
import datetime  # Add this missing import

from utils.report_generator import PatientReportGenerator

class PatientReportDialog(QDialog):
    """Dialog for generating a patient report"""
    
    def __init__(self, config_manager, patient_data, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.patient_data = patient_data
        self.patient_id = patient_data.get("id", "")
        
        # Set dialog properties
        self.setWindowTitle("Generate Patient Report")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Patient info
        info_layout = QHBoxLayout()
        patient_name = self.patient_data.get("name", "Unknown")
        patient_id = self.patient_data.get("id", "Unknown")
        
        info_label = QLabel(f"Generate Report for: {patient_name} (ID: {patient_id})")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(info_label)
        
        main_layout.addLayout(info_layout)
        
        # Options group
        options_group = QGroupBox("Report Options")
        options_layout = QVBoxLayout(options_group)
        
        # Include visit history
        self.include_visits_cb = QCheckBox("Include Visit History")
        self.include_visits_cb.setChecked(True)
        options_layout.addWidget(self.include_visits_cb)
        
        # Include test results
        self.include_tests_cb = QCheckBox("Include Test Results")
        self.include_tests_cb.setChecked(True)
        options_layout.addWidget(self.include_tests_cb)
        
        # Include doctor notes section
        self.include_notes_cb = QCheckBox("Include Section for Doctor's Notes")
        self.include_notes_cb.setChecked(True)
        options_layout.addWidget(self.include_notes_cb)
        
        # Limit to recent visits/tests
        self.recent_only_cb = QCheckBox("Include only recent data (last 12 months)")
        self.recent_only_cb.setChecked(True)
        options_layout.addWidget(self.recent_only_cb)
        
        main_layout.addWidget(options_group)
        
        # Add explanatory text
        info_text = ("The report will be generated as a Word document (.docx) and opened automatically. "
                   "You can then save it to your desired location.")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self._generate_report)
        buttons_layout.addWidget(generate_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _generate_report(self):
        """Generate the patient report"""
        try:
            # Show progress dialog
            progress = QProgressDialog("Generating patient report...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Generating Report")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(300)  # Only show if generation takes longer than 300ms
            progress.setValue(0)
            
            # Create report generator
            report_generator = PatientReportGenerator(self.config_manager)
            
            # Get the patient's data
            from models.patient_manager import PatientManager
            from models.test_results_manager import TestResultsManager
            
            patient_manager = PatientManager(self.config_manager)
            test_results_manager = TestResultsManager(self.config_manager)
            
            progress.setValue(20)
            
            # Get visit history if requested
            visit_history = None
            if self.include_visits_cb.isChecked():
                visit_history = patient_manager.get_visit_history(self.patient_id)
                
                # Filter to recent if requested
                if self.recent_only_cb.isChecked():
                    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=365)
                    visit_history = [
                        visit for visit in visit_history
                        if self._is_date_recent(visit.get("end_time", ""), cutoff_date)
                    ]
            
            progress.setValue(40)
            
            # Get test results if requested
            test_results = None
            if self.include_tests_cb.isChecked():
                test_results = test_results_manager.get_patient_test_results(self.patient_id)
                
                # Filter to recent if requested
                if self.recent_only_cb.isChecked():
                    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=365)
                    test_results = [
                        result for result in test_results
                        if self._is_date_recent(result.get("test_date", ""), cutoff_date)
                    ]
            
            progress.setValue(60)
            
            # Generate the report
            report_file = report_generator.generate_report(
                self.patient_data,
                visit_history=visit_history,
                test_results=test_results,
                include_doctor_notes=self.include_notes_cb.isChecked()
            )
            
            progress.setValue(80)
            
            # Open the report file
            if os.path.exists(report_file):
                self._open_file(report_file)
                progress.setValue(100)
                
                # Wait a brief moment to show 100% before closing progress
                QTimer.singleShot(300, progress.close)
                
                QMessageBox.information(
                    self,
                    "Report Generated",
                    f"Patient report has been generated and opened.\n\nFile: {report_file}"
                )
                self.accept()
            else:
                progress.close()
                QMessageBox.warning(
                    self,
                    "Report Generation Failed",
                    "Failed to generate the report file."
                )
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_exception(e, "Generating patient report", parent=self)
            else:
                self.config_manager.logger.error(f"Error generating patient report: {str(e)}")
                
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while generating the report: {str(e)}"
                )
    
    def _is_date_recent(self, date_str, cutoff_date):
        """Check if a date string is more recent than the cutoff date"""
        if not date_str:
            return False
            
        try:
            date_obj = datetime.datetime.fromisoformat(date_str)
            return date_obj >= cutoff_date
        except Exception as e:
            self.config_manager.logger.warning(f"Failed to parse date {date_str}: {str(e)}")
            return False  # If date can't be parsed, assume it's not recent
    
    def _open_file(self, file_path):
        """Open a file with the default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            self.config_manager.logger.error(f"Error opening file {file_path}: {str(e)}")
            QMessageBox.warning(
                self,
                "Error Opening File",
                f"The report was generated but could not be opened automatically: {str(e)}\n\nFile location: {file_path}"
            )