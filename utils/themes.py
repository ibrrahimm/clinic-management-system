# utils/themes.py
from PySide6.QtCore import QFile, QTextStream, QSettings

def load_stylesheet(is_dark_mode):
    """Load and return the appropriate stylesheet based on theme"""
    if is_dark_mode:
        # Dark theme
        return """
        QMainWindow, QDialog {
            background-color: #2d2d2d;
            color: #f0f0f0;
        }
        QWidget {
            background-color: #2d2d2d;
            color: #f0f0f0;
        }
        QTabWidget::pane {
            border: 1px solid #444444;
            background-color: #2d2d2d;
        }
        QTabWidget::tab-bar {
            left: 5px;
        }
        QTabBar::tab {
            background-color: #3d3d3d;
            color: #f0f0f0;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #4a86e8;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QPushButton {
            background-color: #4a86e8;
            color: white;
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #5a96f8;
        }
        QPushButton:pressed {
            background-color: #3a76d8;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #3d3d3d;
            color: #f0f0f0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox {
            background-color: #3d3d3d;
            color: #f0f0f0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #555555;
            border-left-style: solid;
        }
        QComboBox QAbstractItemView {
            background-color: #3d3d3d;
            color: #f0f0f0;
            selection-background-color: #4a86e8;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #f0f0f0;
        }
        QMenuBar::item {
            background: transparent;
        }
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #f0f0f0;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #4a86e8;
        }
        QHeaderView::section {
            background-color: #3d3d3d;
            color: #f0f0f0;
            padding: 5px;
            border: 1px solid #555555;
        }
        QTableView {
            background-color: #2d2d2d;
            color: #f0f0f0;
            gridline-color: #555555;
            selection-background-color: #4a86e8;
            selection-color: white;
        }
        QTableView::item {
            padding: 5px;
        }
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 14px;
            margin: 14px 0 14px 0;
        }
        QScrollBar::handle:vertical {
            background-color: #5d5d5d;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 14px;
            margin: 0 14px 0 14px;
        }
        QScrollBar::handle:horizontal {
            background-color: #5d5d5d;
            min-width: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
        }
        QToolBar {
            background-color: #3d3d3d;
            border-bottom: 1px solid #555555;
        }
        QStatusBar {
            background-color: #3d3d3d;
            color: #f0f0f0;
        }
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: #f0f0f0;
        }
        QCheckBox, QRadioButton {
            color: #f0f0f0;
        }
        QLabel {
            color: #f0f0f0;
        }
        """
    else:
        # Light theme
        return """
        QMainWindow, QDialog {
            background-color: #f5f5f5;
            color: #333333;
        }
        QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        QTabWidget::tab-bar {
            left: 5px;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333333;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #4a86e8;
            color: white;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QPushButton {
            background-color: #4a86e8;
            color: white;
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #5a96f8;
        }
        QPushButton:pressed {
            background-color: #3a76d8;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: white;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox {
            background-color: white;
            color: #333333;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #cccccc;
            border-left-style: solid;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #333333;
            selection-background-color: #4a86e8;
            selection-color: white;
        }
        QMenuBar {
            background-color: #f5f5f5;
            color: #333333;
        }
        QMenuBar::item {
            background: transparent;
        }
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: white;
            color: #333333;
            border: 1px solid #cccccc;
        }
        QMenu::item:selected {
            background-color: #4a86e8;
            color: white;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            color: #333333;
            padding: 5px;
            border: 1px solid #cccccc;
        }
        QTableView {
            background-color: white;
            color: #333333;
            gridline-color: #dddddd;
            selection-background-color: #4a86e8;
            selection-color: white;
        }
        QTableView::item {
            padding: 5px;
        }
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 14px;
            margin: 14px 0 14px 0;
        }
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            background-color: #f5f5f5;
            height: 14px;
            margin: 0 14px 0 14px;
        }
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            min-width: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
        }
        QToolBar {
            background-color: #f0f0f0;
            border-bottom: 1px solid #cccccc;
        }
        QStatusBar {
            background-color: #f0f0f0;
            color: #333333;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: #333333;
        }
        QCheckBox, QRadioButton {
            color: #333333;
        }
        QLabel {
            color: #333333;
        }
        """

def apply_theme(widget, is_dark_mode=None):
    """Apply theme to a widget"""
    # If no theme specified, get from settings
    if is_dark_mode is None:
        settings = QSettings("MedicalClinic", "AppSettings")
        is_dark_mode = settings.value("dark_mode", False, type=bool)
    
    # Load and apply stylesheet
    stylesheet = load_stylesheet(is_dark_mode)
    widget.setStyleSheet(stylesheet)

def toggle_theme(widget):
    """Toggle theme and apply to widget"""
    settings = QSettings("MedicalClinic", "AppSettings")
    is_dark_mode = settings.value("dark_mode", False, type=bool)
    
    # Toggle and save
    is_dark_mode = not is_dark_mode
    settings.setValue("dark_mode", is_dark_mode)
    
    # Apply
    apply_theme(widget, is_dark_mode)
    
    return is_dark_mode

def get_theme_mode():
    """Get current theme mode (dark or light)"""
    settings = QSettings("MedicalClinic", "AppSettings")
    return settings.value("dark_mode", False, type=bool)