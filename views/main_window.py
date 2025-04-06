# views/main_window.py - Updated version with new features
import os
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, 
                              QHBoxLayout, QWidget, QLabel, QPushButton, QProgressDialog,
                              QStatusBar, QToolBar, QMenuBar, QMenu, QSizePolicy, QFileDialog)
from PySide6.QtCore import Qt, QSize, QSettings, Signal, QTimer
from PySide6.QtGui import QIcon, QPixmap, QAction

from utils.themes import apply_theme, toggle_theme
from views.patients_view import PatientsView
from views.active_visits_view import ActiveVisitsView
from views.reports_view import ReportsView
from views.setup_view import SetupView
from views.enhanced_dashboard_view import EnhancedDashboardView
from views.appointment_view import AppointmentView
from utils.error_handler import ErrorHandler


class MainWindow(QMainWindow):
    """Main application window for Medical Clinic Management System"""
    
    logout_requested = Signal()  # Signal to trigger logout process
    
    def __init__(self, config_manager, current_user, user_role, error_handler=None):
        super().__init__()
        
        # Store references
        self.config_manager = config_manager
        self.current_user = current_user
        self.user_role = user_role
        self.error_handler = error_handler
        
        # Setup window properties
        self.setWindowTitle("Medical Clinic Management System")
        self.setMinimumSize(1200, 700)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "assets", "icons", "clinic_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Apply theme
        apply_theme(self)
        
        # Initialize UI
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_central_widget()
        
        # Setup backup timer
        self._setup_backup_timer()
        
        # Load settings
        self._load_window_settings()
        
        # Show initialization status
        self.statusBar().showMessage("Application initialized", 3000)  # Show for 3 seconds

    
    def _setup_backup_timer(self):
        """Set up timer for scheduled backups"""
        self.backup_timer = QTimer(self)
        # Connect to a backup method
        self.backup_timer.timeout.connect(self._perform_scheduled_backup)
        
        # Set timer to run once every 24 hours (86400000 ms)
        self.backup_timer.start(86400000)
        
        # Also perform a backup on startup
        QTimer.singleShot(60000, self._perform_scheduled_backup)  # 1 minute after startup
        
        
    def _perform_scheduled_backup(self):
        """Perform a scheduled backup"""
        try:
            backup_file, error = self.config_manager.create_scheduled_backup()
            
            if backup_file:
                self.statusBar().showMessage(f"Automatic backup created: {backup_file}", 5000)
            else:
                self.statusBar().showMessage(f"Automatic backup failed: {error}", 5000)
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_exception(e, "Performing scheduled backup", parent=self)   
        
        
    def restore_from_backup(self):
        """Restore the system from a backup file"""
        try:
            # Ask for backup file
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", "", "Backup Files (*.zip);;All Files (*.*)")
            
            if not file_path:
                return  # User cancelled
            
            # Confirm restoration
            confirm = QMessageBox.question(
                self,
                "Confirm Restoration",
                "Restoring from backup will replace all current data. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm != QMessageBox.Yes:
                return
            
            # Show progress
            progress = QProgressDialog("Restoring from backup...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            # Perform restoration
            success, message = self.config_manager.restore_backup(file_path)
            
            progress.setValue(100)
            
            if success:
                QMessageBox.information(self, "Restoration Complete", message)
                # Refresh all views
                self.refresh_all()
            else:
                QMessageBox.critical(self, "Restoration Failed", message)
        except Exception as e:
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_exception(e, "Restoring from backup", parent=self)
            else:
                QMessageBox.critical(self, "Error", f"Failed to restore from backup: {str(e)}")
    
    
    
    def _setup_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Add actions to file menu
        refresh_action = QAction(QIcon(), "&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        # Add backup action for admin users
        if self.user_role == "admin":
            backup_action = QAction(QIcon(), "Create &Backup", self)
            backup_action.triggered.connect(self.create_backup)
            file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction(QIcon(), "E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Theme action in view menu
        self.theme_action = QAction("Toggle &Dark Mode", self)
        self.theme_action.setCheckable(True)
        
        # Check current theme from settings
        settings = QSettings("MedicalClinic", "AppSettings")
        dark_mode = settings.value("dark_mode", False, type=bool)
        self.theme_action.setChecked(dark_mode)
        
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        
        #Backup
        backup_menu = file_menu.addMenu("&Backup && Restore")

        create_backup_action = QAction("Create &Manual Backup", self)
        create_backup_action.triggered.connect(self.create_backup)
        backup_menu.addAction(create_backup_action)
        
        if hasattr(self, '_perform_scheduled_backup'):
            scheduled_backup_action = QAction(QIcon(), "Create &Scheduled Backup", self)
            scheduled_backup_action.triggered.connect(self._perform_scheduled_backup)
            backup_menu.addAction(scheduled_backup_action)
        
        backup_menu.addSeparator()

        restore_backup_action = QAction("&Restore from Backup", self)
        restore_backup_action.triggered.connect(self.restore_from_backup)
        backup_menu.addAction(restore_backup_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Create the application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Load icon for toolbar if available
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "assets", "icons", "clinic_icon.png")
        
        # Add app logo at the beginning of toolbar
        logo_label = QLabel()
        
        if os.path.exists(icon_path):
            logo_pixmap = QPixmap(icon_path)
            logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        toolbar.addWidget(logo_label)
        
        # Add app name after logo
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        app_name_label = QLabel(clinic_name)
        app_name_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 0 10px;")
        toolbar.addWidget(app_name_label)
        
        # Add spacer to push user info to right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # User information display
        user_display_name = self.config_manager.users.get(self.current_user, {}).get("name", self.current_user)
        user_label = QLabel(f"User: {user_display_name} ({self.user_role})")
        toolbar.addWidget(user_label)
        
        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        toolbar.addWidget(logout_button)
    
    def _setup_status_bar(self):
        """Create the status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Add time label to right side
        self.time_label = QLabel()
        status_bar.addPermanentWidget(self.time_label)
        
        # Update time
        self._update_time()
    
    def _setup_central_widget(self):
        """Create the central widget with tab views"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add dashboard view as the first tab
        self.dashboard_view = EnhancedDashboardView(self.config_manager, self.current_user, self.user_role)
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
       
       # Connect dashboard navigation signals
        self.dashboard_view.navigate_to_patients.connect(lambda: self.tab_widget.setCurrentWidget(self.patients_view))
        self.dashboard_view.navigate_to_appointments.connect(lambda: self.tab_widget.setCurrentWidget(self.appointment_view))
        self.dashboard_view.navigate_to_visits.connect(lambda: self.tab_widget.setCurrentWidget(self.active_visits_view))
        self.dashboard_view.navigate_to_reports.connect(lambda: self.tab_widget.setCurrentWidget(self.reports_view))
        
        
        # Add patients view tab
        self.patients_view = PatientsView(self.config_manager, self.current_user, self.user_role)
        self.tab_widget.addTab(self.patients_view, "Patients")
        
        # Add appointments view
        self.appointment_view = AppointmentView(self.config_manager, self.current_user, self.user_role)
        self.tab_widget.addTab(self.appointment_view, "Appointments")
        
        # Add active visits tab
        self.active_visits_view = ActiveVisitsView(self.config_manager, self.current_user, self.user_role)
        self.tab_widget.addTab(self.active_visits_view, "Active Visits")
        
        # Add reports tab
        self.reports_view = ReportsView(self.config_manager, self.current_user)
        self.tab_widget.addTab(self.reports_view, "Reports")
        
        # Add admin tabs if user is admin
        if self.user_role == "admin":
            self.setup_view = SetupView(self.config_manager)
            self.tab_widget.addTab(self.setup_view, "Setup")
            
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _load_window_settings(self):
        """Load window position and size from settings"""
        settings = QSettings("MedicalClinic", "AppSettings")
        
        # Window geometry
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Window state
        state = settings.value("window_state")
        if state:
            self.restoreState(state)
    
    def _save_window_settings(self):
        """Save window position and size to settings"""
        settings = QSettings("MedicalClinic", "AppSettings")
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
    
    def _update_time(self):
        """Update the time display in status bar"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
        
        # Schedule next update
        QTimer.singleShot(1000, self._update_time)
    
    def _on_tab_changed(self, index):
        """Handle tab changed event"""
        # Refresh the selected tab view
        current_tab = self.tab_widget.widget(index)
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
    
    def toggle_theme(self, checked):
        """Toggle between light and dark themes"""
        settings = QSettings("MedicalClinic", "AppSettings")
        settings.setValue("dark_mode", checked)
        
        apply_theme(self, checked)
    
    def refresh_all(self):
        """Refresh all views"""
        try:
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
        
            self.statusBar().showMessage("Refreshed", 2000)
            
        except Exception as e:
            self.error_handler.handle_exception(e, "Refreshing views", parent=self)
    
    def create_backup(self):
        """Create a manual backup"""
        try:
            success = self.config_manager.create_manual_backup()
            if success:
                self.statusBar().showMessage("Backup created successfully", 3000)
            else:
                self.statusBar().showMessage("Backup failed", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)
    
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        clinic_name = self.config_manager.config.get("clinic_name", "Medical Clinic")
        
        QMessageBox.about(self, f"About {clinic_name} Management System",
                         f"{clinic_name} Management System v2.0.0\n\n"
                         "A comprehensive patient and visit management system.\n\n"
                         "© 2025 Medical Software Solutions")
    
    def logout(self):
        """Log out from the application"""
        # Emit signal to notify parent
        self.logout_requested.emit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window settings
        self._save_window_settings()
        
        # Accept the event
        event.accept()