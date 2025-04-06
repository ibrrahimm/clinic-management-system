# main.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

from models.config_manager import ConfigManager
from views.login_window import LoginWindow
from views.main_window import MainWindow
from utils.error_handler import ErrorHandler


def main():
    """Application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Clinic Management System")
    app.setOrganizationName("Medical Clinic")
    app.setOrganizationDomain("medicalclinic.com")
    
    # Set application style (can be overridden by theme)
    app.setStyle("Fusion")
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Initialize error handler
    error_handler = ErrorHandler(config_manager)
    
    # Install global exception handler
    error_handler.install_global_handler()
    

    # Create login window
    login_window = LoginWindow(config_manager)

    # Create main window (hidden initially)
    main_window = None
    
    # Connect login signal
    def on_login_successful(username, role):
        """Handle successful login"""
        nonlocal main_window
        # Create and show main window
        main_window = MainWindow(config_manager, username, role, error_handler=error_handler)
        main_window.show()
    
    login_window.login_successful.connect(on_login_successful)
    
    # Show login window
    login_window.show()
    
    # Start application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    # Check dependencies before starting the application
   # from utils.dependency_checker import DependencyChecker
  #  if not DependencyChecker.check_and_install():
     #   print("Exiting due to missing dependencies.")
    #    sys.exit(1)
        
    main()