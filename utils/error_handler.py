# utils/error_handler.py
import traceback
import sys
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QFileDialog
from PySide6.QtCore import Qt

class ErrorHandler:
    """
    Centralized error handling for the clinic management system.
    Provides consistent error reporting, logging, and user notification.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the error handler
        
        Args:
            config_manager: Reference to the application's config manager for logging
        """
        self.config_manager = config_manager
        self.logger = config_manager.logger
    
    def handle_exception(self, exception, context="", show_error=True, parent=None):
        """
        Handle an exception with logging and optional user notification
        
        Args:
            exception: The exception object
            context: String describing where the error occurred
            show_error: Whether to show an error dialog to the user
            parent: Parent widget for the error dialog (if any)
            
        Returns:
            False (to facilitate error handling in conditional statements)
        """
        # Get full traceback
        error_details = traceback.format_exc()
        
        # Log the error
        self.logger.error(f"Error in {context}: {str(exception)}")
        self.logger.error(error_details)
        
        # Show error message if requested
        if show_error:
            QMessageBox.critical(
                parent,  # Parent window (can be None)
                "Error",
                f"An error occurred: {str(exception)}\n\nContext: {context}"
            )
        
        return False
    
    def handle_error(self, message, context="", show_error=True, parent=None, error_level="error"):
        """
        Handle a non-exception error with logging and optional user notification
        
        Args:
            message: Error message
            context: String describing where the error occurred
            show_error: Whether to show an error dialog to the user
            parent: Parent widget for the error dialog (if any)
            error_level: Logging level (error, warning, info)
            
        Returns:
            False (to facilitate error handling in conditional statements)
        """
        # Log the error
        if error_level == "error":
            self.logger.error(f"Error in {context}: {message}")
        elif error_level == "warning":
            self.logger.warning(f"Warning in {context}: {message}")
        else:
            self.logger.info(f"Info in {context}: {message}")
        
        # Show error message if requested
        if show_error:
            QMessageBox.critical(
                parent,  # Parent window (can be None)
                "Error",
                f"{message}\n\nContext: {context}"
            )
        
        return False
    
    def install_global_handler(self):
        """
        Install a global exception handler to catch unhandled exceptions
        """
        def global_exception_handler(exctype, value, tb):
            """Global exception handler for unhandled exceptions"""
            # Log the error
            error_details = ''.join(traceback.format_exception(exctype, value, tb))
            self.logger.critical(f"Unhandled exception: {error_details}")
            
            # Show error dialog
            QMessageBox.critical(
                None,
                "Critical Error",
                f"An unhandled error occurred: {str(value)}\n\n"
                f"The application may be unstable. Please save your work and restart."
            )
            
            # Call the default handler
            sys.__excepthook__(exctype, value, tb)
        
        # Set the global exception hook
        sys.excepthook = global_exception_handler

# Usage example:
# try:
#     # Some code that might raise an exception
#     result = potentially_failing_function()
# except Exception as e:
#     self.error_handler.handle_exception(e, "Performing operation X", parent=self)
#     return