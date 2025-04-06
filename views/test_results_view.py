# views/test_results_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QDialog, QFormLayout, QTextEdit,
                             QDateEdit, QComboBox, QMessageBox, QHeaderView,
                             QMenu, QSpinBox, QDoubleSpinBox, QTabWidget,
                             QSplitter, QFrame, QFileDialog)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QCursor

import datetime
import uuid
import json
import sys

from models.patient_manager import PatientManager
from models.test_results_manager import TestResultsManager
from utils.validators import Validator

class TestResultEntryDialog(QDialog):
    """Dialog for entering or editing a test result"""
    
    def __init__(self, config_manager, patient_id=None, result_data=None, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.patient_id = patient_id
        self.result_data = result_data or {}
        
        # Create test results manager
        self.test_results_manager = TestResultsManager(config_manager)
        
        # Set dialog properties
        self.setWindowTitle("Test Result")
        self.setMinimumSize(500, 400)
        
        # Setup UI
        self._setup_ui()
        
        # Load test result data if provided
        if result_data:
            self._load_result_data()
    
    def _setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Test name/type
        self.test_name_combo = QComboBox()
        self.test_name_combo.setEditable(True)
        
        # Get existing test types
        test_types = self.test_results_manager.get_test_types()
        self.test_name_combo.addItems(test_types)
        
        # Add common test types if not already in the list
        common_tests = [
            "Complete Blood Count (CBC)",
            "Basic Metabolic Panel (BMP)",
            "Comprehensive Metabolic Panel (CMP)",
            "Lipid Panel",
            "Liver Function Tests",
            "Thyroid Function Tests",
            "Hemoglobin A1C",
            "Urinalysis",
            "Blood Glucose",
            "Vitamin D",
            "Iron Panel",
            "COVID-19 Test"
        ]
        
        for test in common_tests:
            if test not in test_types:
                self.test_name_combo.addItem(test)
        
        form_layout.addRow("Test Name:", self.test_name_combo)
        
        # Test date
        self.test_date_edit = QDateEdit()
        self.test_date_edit.setCalendarPopup(True)
        self.test_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Test Date:", self.test_date_edit)
        
        # Test value
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Enter test result value")
        form_layout.addRow("Value:", self.value_edit)
        
        # Unit
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("e.g., mg/dL, mmol/L")
        form_layout.addRow("Unit:", self.unit_edit)
        
        # Reference range
        self.reference_range_edit = QLineEdit()
        self.reference_range_edit.setPlaceholderText("e.g., 70-99, <200")
        form_layout.addRow("Reference Range:", self.reference_range_edit)
        
        # Is normal
        self.is_normal_combo = QComboBox()
        self.is_normal_combo.addItems(["Normal", "Abnormal", "Unknown"])
        form_layout.addRow("Result Status:", self.is_normal_combo)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter any additional notes or details about the test result")
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Ordered by
        self.ordered_by_edit = QLineEdit()
        form_layout.addRow("Ordered By:", self.ordered_by_edit)
        
        # Lab/facility
        self.lab_edit = QLineEdit()
        form_layout.addRow("Lab/Facility:", self.lab_edit)
        
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
    
    def _load_result_data(self):
        """Load test result data into the form"""
        # Test name
        test_name = self.result_data.get("test_name", "")
        index = self.test_name_combo.findText(test_name)
        if index >= 0:
            self.test_name_combo.setCurrentIndex(index)
        else:
            self.test_name_combo.setCurrentText(test_name)
        
        # Test date
        test_date_str = self.result_data.get("test_date", "")
        if test_date_str:
            try:
                date_obj = datetime.datetime.fromisoformat(test_date_str).date()
                self.test_date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                # Use current date if parsing fails
                self.test_date_edit.setDate(QDate.currentDate())
        
        # Value
        self.value_edit.setText(str(self.result_data.get("value", "")))
        
        # Unit
        self.unit_edit.setText(self.result_data.get("unit", ""))
        
        # Reference range
        self.reference_range_edit.setText(self.result_data.get("reference_range", ""))
        
        # Is normal
        is_normal = self.result_data.get("is_normal", "Unknown")
        index = self.is_normal_combo.findText(is_normal)
        if index >= 0:
            self.is_normal_combo.setCurrentIndex(index)
        
        # Notes
        self.notes_edit.setText(self.result_data.get("notes", ""))
        
        # Ordered by
        self.ordered_by_edit.setText(self.result_data.get("ordered_by", ""))
        
        # Lab
        self.lab_edit.setText(self.result_data.get("lab", ""))
    
    def get_result_data(self):
        """Get test result data from the form"""
        # Validate required fields
        test_name = self.test_name_combo.currentText().strip()
        if not test_name:
            QMessageBox.warning(self, "Input Error", "Test name is required.")
            return None
        
        # Get test date
        test_date = self.test_date_edit.date().toString(Qt.ISODate)
        
        # Create result data dictionary
        result_data = {
            "test_name": test_name,
            "test_date": test_date,
            "value": self.value_edit.text().strip(),
            "unit": self.unit_edit.text().strip(),
            "reference_range": self.reference_range_edit.text().strip(),
            "is_normal": self.is_normal_combo.currentText(),
            "notes": self.notes_edit.toPlainText(),
            "ordered_by": self.ordered_by_edit.text().strip(),
            "lab": self.lab_edit.text().strip()
        }
        
        # If editing, preserve the ID
        if "id" in self.result_data:
            result_data["id"] = self.result_data["id"]
        
        return result_data


class TestResultsTable(QTableWidget):
    """Custom table widget for displaying test results"""
    
    result_selected = Signal(str)  # Signal when a result is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up table properties
        self.setColumnCount(7)  # Date, Test Name, Value, Unit, Reference Range, Status, Actions
        self.setHorizontalHeaderLabels(["Date", "Test Name", "Value", "Unit", "Reference Range", "Status", ""])
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Test Name
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Value
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Unit
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Reference Range
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        # Connect double-click signal
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
    
    def populate_results(self, results):
        """Populate table with test results"""
        # Clear existing data
        self.setRowCount(0)
        
        # Add results to table
        for row, result in enumerate(results):
            self.insertRow(row)
            
            # Date
            test_date_str = result.get("test_date", "")
            if test_date_str:
                try:
                    date_obj = datetime.datetime.fromisoformat(test_date_str).date()
                    date_display = date_obj.strftime("%Y-%m-%d")
                except:
                    date_display = test_date_str
            else:
                date_display = "Unknown"
                
            date_item = QTableWidgetItem(date_display)
            date_item.setData(Qt.UserRole, result.get("id", ""))  # Store result ID
            self.setItem(row, 0, date_item)
            
            # Test Name
            test_name = result.get("test_name", "Unknown")
            test_item = QTableWidgetItem(test_name)
            self.setItem(row, 1, test_item)
            
            # Value
            value = result.get("value", "")
            value_item = QTableWidgetItem(str(value))
            self.setItem(row, 2, value_item)
            
            # Unit
            unit = result.get("unit", "")
            unit_item = QTableWidgetItem(unit)
            self.setItem(row, 3, unit_item)
            
            # Reference Range
            ref_range = result.get("reference_range", "")
            range_item = QTableWidgetItem(ref_range)
            self.setItem(row, 4, range_item)
            
            # Status
            status = result.get("is_normal", "Unknown")
            status_item = QTableWidgetItem(status)
            
            if status == "Normal":
                status_item.setForeground(QColor(0, 128, 0))  # Green
            elif status == "Abnormal":
                status_item.setForeground(QColor(255, 0, 0))  # Red
                
            self.setItem(row, 5, status_item)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.setProperty("result_id", result.get("id", ""))
            view_btn.clicked.connect(self._on_view_clicked)
            self.setCellWidget(row, 6, view_btn)
    
    def _on_cell_double_clicked(self, row, column):
        """Handle double-click on a table cell"""
        result_id = self.item(row, 0).data(Qt.UserRole)
        if result_id:
            self.result_selected.emit(result_id)
    
    def _on_view_clicked(self):
        """Handle view button click"""
        button = self.sender()
        if button:
            result_id = button.property("result_id")
            if result_id:
                self.result_selected.emit(result_id)


class TestResultsChart(QFrame):
    """Widget for displaying a chart of test results over time"""
    
    def __init__(self, title="Test Results Trend", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.data_points = []  # List of (date, value) tuples
        self.y_label = ""
        self.unit = ""
        self.reference_min = None
        self.reference_max = None
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(400, 300)
        
        # Default colors
        self.line_color = QColor(0, 120, 215)  # Blue
        self.point_color = QColor(0, 120, 215)
        self.reference_line_color = QColor(255, 0, 0, 128)  # Semi-transparent red
    
    def set_data(self, data_points, y_label="Value", unit="", ref_min=None, ref_max=None):
        """Set the data points to be displayed in the chart"""
        self.data_points = data_points
        self.y_label = y_label
        self.unit = unit
        self.reference_min = ref_min
        self.reference_max = ref_max
        
        # Force redraw
        self.update()
    
    def paintEvent(self, event):
        """Paint the chart"""
        super().paintEvent(event)
        
        if not self.data_points:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get chart area
        chart_rect = self.rect().adjusted(50, 50, -20, -30)
        
        # Draw title
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(self.rect().adjusted(0, 10, 0, 0), Qt.AlignHCenter, self.title)
        
        # Find min and max values for scaling
        values = [point["value"] for point in self.data_points]
        min_value = min(values) if values else 0
        max_value = max(values) if values else 100
        
        # Adjust min and max to include reference ranges
        if self.reference_min is not None and self.reference_min < min_value:
            min_value = self.reference_min
        if self.reference_max is not None and self.reference_max > max_value:
            max_value = self.reference_max
        
        # Add padding to min and max
        value_range = max_value - min_value
        min_value -= value_range * 0.1
        max_value += value_range * 0.1
        
        if min_value == max_value:  # Handle case where all values are the same
            min_value -= 1
            max_value += 1
        
        # Draw y-axis
        painter.setPen(QPen(Qt.black))
        painter.drawLine(chart_rect.left(), chart_rect.top(), chart_rect.left(), chart_rect.bottom())
        
        # Draw y-axis label
        painter.save()
        painter.translate(10, chart_rect.center().y())
        painter.rotate(-90)
        label_text = f"{self.y_label} ({self.unit})" if self.unit else self.y_label
        painter.drawText(0, 0, label_text)
        painter.restore()
        
        # Draw y-axis tick marks and values
        num_ticks = 5
        for i in range(num_ticks + 1):
            y = chart_rect.bottom() - (i / num_ticks) * chart_rect.height()
            tick_value = min_value + (i / num_ticks) * (max_value - min_value)
            
            # Draw tick mark
            painter.drawLine(chart_rect.left() - 5, y, chart_rect.left(), y)
            
            # Draw tick value
            value_text = f"{tick_value:.1f}"
            painter.drawText(chart_rect.left() - 40, y + 5, value_text)
        
        # Draw x-axis
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())
        
        # Draw x-axis label (Time)
        painter.drawText(
            chart_rect.center().x() - 20,
            chart_rect.bottom() + 25,
            "Date"
        )
        
        # Draw x-axis tick marks and dates
        if len(self.data_points) > 1:
            dates = [point["date"] for point in self.data_points]
            min_date = min(dates)
            max_date = max(dates)
            date_range = (max_date - min_date).days
            
            # Determine how many date labels to show
            max_labels = min(len(self.data_points), 5)
            
            for i in range(max_labels):
                if date_range > 0:
                    # Evenly space the labels
                    days_offset = (i / (max_labels - 1)) * date_range
                    date = min_date + datetime.timedelta(days=days_offset)
                else:
                    # If all dates are the same, just show one date
                    date = min_date
                
                x = chart_rect.left() + (i / (max_labels - 1)) * chart_rect.width()
                
                # Draw tick mark
                painter.drawLine(x, chart_rect.bottom(), x, chart_rect.bottom() + 5)
                
                # Draw date
                date_text = date.strftime("%Y-%m-%d")
                
                # Create a bounding rectangle for the text to center it under the tick
                text_rect = painter.fontMetrics().boundingRect(date_text)
                text_rect.moveCenter(painter.fontMetrics().boundingRect(date_text).center())
                text_rect.moveTop(chart_rect.bottom() + 5)
                text_rect.moveLeft(int(x) - text_rect.width() // 2)
                
                painter.drawText(text_rect, date_text)
        
        # Draw reference range lines if provided
        if self.reference_min is not None or self.reference_max is not None:
            painter.setPen(QPen(self.reference_line_color, 1, Qt.DashLine))
            
            if self.reference_min is not None:
                y = chart_rect.bottom() - ((self.reference_min - min_value) / (max_value - min_value)) * chart_rect.height()
                painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
                painter.drawText(chart_rect.right() - 50, y - 5, f"Min: {self.reference_min}")
            
            if self.reference_max is not None:
                y = chart_rect.bottom() - ((self.reference_max - min_value) / (max_value - min_value)) * chart_rect.height()
                painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
                painter.drawText(chart_rect.right() - 50, y - 5, f"Max: {self.reference_max}")
        
        # Draw data points and connecting lines
        if len(self.data_points) > 0:
            # Calculate point positions
            points = []
            
            for point in self.data_points:
                # Calculate x position based on date
                if len(self.data_points) > 1:
                    date_position = (point["date"] - min_date).total_seconds() / (max_date - min_date).total_seconds()
                else:
                    date_position = 0.5  # Center if only one point
                
                x = chart_rect.left() + date_position * chart_rect.width()
                
                # Calculate y position based on value
                value_position = (point["value"] - min_value) / (max_value - min_value)
                y = chart_rect.bottom() - value_position * chart_rect.height()
                
                points.append((x, y, point))
            
            # Draw lines connecting points
            if len(points) > 1:
                painter.setPen(QPen(self.line_color, 2))
                
                for i in range(len(points) - 1):
                    x1, y1, _ = points[i]
                    x2, y2, _ = points[i + 1]
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
            # Draw points
            for x, y, point in points:
                # Draw circle for each point
                painter.setPen(QPen(self.point_color, 2))
                painter.setBrush(Qt.white)
                painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
                
                # Draw value near the point
                painter.setPen(Qt.black)
                value_text = f"{point['value']}"
                painter.drawText(int(x) - 15, int(y) - 10, value_text)


class PatientTestResultsView(QWidget):
    """View for managing test results for a specific patient"""
    
    def __init__(self, config_manager, patient_id=None, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.patient_id = patient_id
        self.patient_name = "Unknown Patient"
        
        # Create managers
        self.test_results_manager = TestResultsManager(config_manager)
        self.patient_manager = PatientManager(config_manager)
        
        # Get patient name if ID provided
        if patient_id:
            patient_data = self.patient_manager.get_patient(patient_id)
            if patient_data:
                self.patient_name = patient_data.get("name", "Unknown Patient")
        
        # Setup UI
        self._setup_ui()
        
        # Load test results if patient ID provided
        if patient_id:
            self.load_patient_results()
    
    def _setup_ui(self):
        """Set up the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Header with patient info and controls
        header_layout = QHBoxLayout()
        
        self.patient_label = QLabel(f"Test Results for: {self.patient_name}")
        self.patient_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.patient_label)
        
        # Add spacer
        header_layout.addStretch(1)
        
        # Add result button
        self.add_result_btn = QPushButton("Add Test Result")
        self.add_result_btn.clicked.connect(self._add_test_result)
        header_layout.addWidget(self.add_result_btn)
        
        # Import results button
        self.import_btn = QPushButton("Import Results")
        self.import_btn.clicked.connect(self._import_results)
        header_layout.addWidget(self.import_btn)
        
        # Export results button
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self._export_results)
        header_layout.addWidget(self.export_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by Test:"))
        
        self.test_filter_combo = QComboBox()
        self.test_filter_combo.addItem("All Tests")
        self.test_filter_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.test_filter_combo)
        
        filter_layout.addWidget(QLabel("Date Range:"))
        
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addMonths(-3))  # Last 3 months
        self.from_date_edit.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.from_date_edit)
        
        filter_layout.addWidget(QLabel("to"))
        
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.to_date_edit)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Clear Filters")
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filters_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Create tab widget for table and chart views
        self.tab_widget = QTabWidget()
        
        # Table tab
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        self.results_table = TestResultsTable()
        self.results_table.result_selected.connect(self._view_test_result)
        table_layout.addWidget(self.results_table)
        
        self.tab_widget.addTab(table_tab, "Table View")
        
        # Chart tab
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)
        
        # Test selection for chart
        chart_controls = QHBoxLayout()
        
        chart_controls.addWidget(QLabel("Select Test for Trending:"))
        
        self.trend_test_combo = QComboBox()
        self.trend_test_combo.currentTextChanged.connect(self._update_chart)
        chart_controls.addWidget(self.trend_test_combo)
        
        chart_layout.addLayout(chart_controls)
        
        # Chart widget
        self.chart_widget = TestResultsChart("Test Results Trend")
        chart_layout.addWidget(self.chart_widget)
        
        self.tab_widget.addTab(chart_tab, "Trend Chart")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
    
    def set_patient(self, patient_id):
        """Set the current patient and reload data"""
        self.patient_id = patient_id
        
        # Update patient name
        if patient_id:
            patient_data = self.patient_manager.get_patient(patient_id)
            if patient_data:
                self.patient_name = patient_data.get("name", "Unknown Patient")
                self.patient_label.setText(f"Test Results for: {self.patient_name}")
        
        # Load test results
        self.load_patient_results()
    
    def load_patient_results(self):
        """Load all test results for the current patient"""
        if not self.patient_id:
            return
        
        # Get all test results
        all_results = self.test_results_manager.get_patient_test_results(self.patient_id)
        
        # Populate test filter dropdown
        self.test_filter_combo.clear()
        self.test_filter_combo.addItem("All Tests")
        
        # Populate trend test dropdown
        self.trend_test_combo.clear()
        
        # Get unique test types
        test_types = set()
        for result in all_results:
            test_type = result.get("test_name")
            if test_type:
                test_types.add(test_type)
        
        # Add to dropdowns
        for test_type in sorted(test_types):
            self.test_filter_combo.addItem(test_type)
            self.trend_test_combo.addItem(test_type)
        
        # Populate table with all results
        self.results_table.populate_results(all_results)
        
        # Update chart if test types are available
        if test_types:
            self.tab_widget.setTabEnabled(1, True)  # Enable chart tab
            self._update_chart(self.trend_test_combo.currentText())
        else:
            self.tab_widget.setTabEnabled(1, False)  # Disable chart tab
        
        # Update status
        self.status_label.setText(f"{len(all_results)} test results")
    
    def _apply_filters(self):
        """Apply filters to the test results table"""
        if not self.patient_id:
            return
        
        test_filter = self.test_filter_combo.currentText()
        from_date = self.from_date_edit.date().toPython()
        to_date = self.to_date_edit.date().toPython()
        
        # Get filtered results
        if test_filter == "All Tests":
            # Filter by date only
            filtered_results = self.test_results_manager.get_test_results_in_range(
                self.patient_id, from_date, to_date)
        else:
            # Filter by test type and date
            all_type_results = self.test_results_manager.get_test_results_by_type(
                self.patient_id, test_filter)
            
            # Then filter by date
            filtered_results = []
            for result in all_type_results:
                test_date_str = result.get("test_date", "")
                if test_date_str:
                    try:
                        test_date = datetime.datetime.fromisoformat(test_date_str).date()
                        if from_date <= test_date <= to_date:
                            filtered_results.append(result)
                    except:
                        # Skip results with invalid dates
                        pass
        
        # Update table
        self.results_table.populate_results(filtered_results)
        
        # Update status
        self.status_label.setText(f"{len(filtered_results)} test results")
    
    def _clear_filters(self):
        """Clear all filters and show all results"""
        # Reset filter controls
        self.test_filter_combo.setCurrentIndex(0)  # "All Tests"
        self.from_date_edit.setDate(QDate.currentDate().addMonths(-3))
        self.to_date_edit.setDate(QDate.currentDate())
        
        # Reload all results
        self.load_patient_results()
    
    def _update_chart(self, test_type):
        """Update the trend chart with data for the selected test type"""
        if not self.patient_id or not test_type:
            return
        
        # Get numerical results for the selected test type
        numerical_results = self.test_results_manager.get_numerical_test_results(
            self.patient_id, test_type)
        
        if not numerical_results:
            # No numerical data available
            self.chart_widget.set_data([], test_type)
            return
        
        # Get unit from the most recent result
        unit = numerical_results[-1]["unit"] if numerical_results else ""
        
        # Try to parse reference range for min/max values
        ref_min = None
        ref_max = None
        
        ref_range = numerical_results[-1].get("reference_range", "")
        if ref_range:
            # Try to parse common reference range formats
            if "-" in ref_range:
                # Format: "min-max"
                parts = ref_range.split("-")
                try:
                    ref_min = float(parts[0].strip())
                    ref_max = float(parts[1].strip())
                except:
                    pass
            elif "<" in ref_range:
                # Format: "< max"
                try:
                    ref_max = float(ref_range.replace("<", "").strip())
                except:
                    pass
            elif ">" in ref_range:
                # Format: "> min"
                try:
                    ref_min = float(ref_range.replace(">", "").strip())
                except:
                    pass
        
        # Update chart
        self.chart_widget.set_data(
            numerical_results, 
            test_type, 
            unit, 
            ref_min, 
            ref_max
        )
    
    def _add_test_result(self):
        """Add a new test result"""
        if not self.patient_id:
            QMessageBox.warning(self, "Error", "No patient selected")
            return
        
        dialog = TestResultEntryDialog(self.config_manager, self.patient_id, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get test result data
            result_data = dialog.get_result_data()
            
            if result_data:
                # Add test result
                success, message = self.test_results_manager.add_test_result(
                    self.patient_id, result_data)
                
                if success:
                    self.status_label.setText("Test result added successfully")
                    self.load_patient_results()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add test result: {message}")
    
    def _view_test_result(self, result_id):
        """View and edit a test result"""
        if not self.patient_id:
            return
        
        # Get test result data
        result_data = self.test_results_manager.get_test_result(self.patient_id, result_id)
        
        if not result_data:
            QMessageBox.warning(self, "Error", "Test result not found")
            return
        
        # Create a popup menu with options
        menu = QMenu(self)
        
        view_action = QAction("View/Edit Result", self)
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Result", self)
        menu.addAction(delete_action)
        
        # Get the global cursor position
        global_pos = QCursor.pos()
        
        # Show menu at cursor position
        action = menu.exec_(global_pos)
        
        if action == view_action:
            self._edit_test_result(result_id, result_data)
        elif action == delete_action:
            self._delete_test_result(result_id)
    
    def _edit_test_result(self, result_id, result_data):
        """Edit an existing test result"""
        # Create copy with ID included
        result_with_id = result_data.copy()
        result_with_id["id"] = result_id
        
        dialog = TestResultEntryDialog(
            self.config_manager, 
            self.patient_id,
            result_data=result_with_id, 
            parent=self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated test result data
            updated_data = dialog.get_result_data()
            
            if updated_data:
                # Update test result
                success, message = self.test_results_manager.update_test_result(
                    self.patient_id, result_id, updated_data)
                
                if success:
                    self.status_label.setText("Test result updated successfully")
                    self.load_patient_results()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update test result: {message}")
    
    def _delete_test_result(self, result_id):
        """Delete a test result"""
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this test result? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.test_results_manager.delete_test_result(
                self.patient_id, result_id)
            
            if success:
                self.status_label.setText("Test result deleted")
                self.load_patient_results()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete test result: {message}")
    
    def _import_results(self):
        """Import test results from a JSON file"""
        if not self.patient_id:
            QMessageBox.warning(self, "Error", "No patient selected")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Test Results", "", "JSON Files (*.json);;All Files (*.*)")
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                imported_results = json.load(f)
            
            if not isinstance(imported_results, list):
                QMessageBox.warning(
                    self, "Import Error", 
                    "Invalid file format. Expected a list of test result objects.")
                return
            
            # Import each result
            success_count = 0
            error_count = 0
            
            for result_data in imported_results:
                # Generate new ID for each result
                if "id" in result_data:
                    del result_data["id"]
                
                # Add result
                success, _ = self.test_results_manager.add_test_result(
                    self.patient_id, result_data)
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
            
            # Reload results
            self.load_patient_results()
            
            # Show import summary
            QMessageBox.information(
                self, "Import Results", 
                f"Import complete.\n\nSuccessfully imported: {success_count}\nErrors: {error_count}")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import results: {str(e)}")
    
    def _export_results(self):
        """Export test results to a JSON file"""
        if not self.patient_id:
            QMessageBox.warning(self, "Error", "No patient selected")
            return
        
        # Get all results for the patient
        results = self.test_results_manager.get_patient_test_results(self.patient_id)
        
        if not results:
            QMessageBox.information(self, "Export", "No test results to export")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Test Results", f"{self.patient_name}_test_results.json", 
            "JSON Files (*.json);;All Files (*.*)")
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Write to JSON file
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            QMessageBox.information(
                self, "Export Complete", 
                f"Successfully exported {len(results)} test results to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")
    
    def refresh(self):
        """Refresh the view"""
        self.load_patient_results()