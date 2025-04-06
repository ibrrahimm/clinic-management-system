# utils/validators.py
import re
import datetime
from PySide6.QtCore import QDate

class Validator:
    """Utility class for data validation throughout the application"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:  # Empty email is considered valid (optional field)
            return True
            
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:  # Empty phone is considered valid (optional field)
            return True
            
        # Allow common phone formats with optional country code
        pattern = r"^(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_date(date_str, date_format="%Y-%m-%d"):
        """Validate date string format"""
        if not date_str:  # Empty date is considered valid (optional field)
            return True
            
        try:
            datetime.datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_object(date, min_date=None, max_date=None):
        """Validate QDate object is within range"""
        if not isinstance(date, QDate):
            return False
            
        if min_date and date < min_date:
            return False
            
        if max_date and date > max_date:
            return False
            
        return True
    
    @staticmethod
    def validate_required_field(value, field_name=None):
        """Validate that a required field is not empty"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            message = "This field is required"
            if field_name:
                message = f"{field_name} is required"
            return False, message
        return True, ""
    
    @staticmethod
    def validate_numeric(value, min_value=None, max_value=None):
        """Validate that a value is numeric and within range"""
        if not value:  # Empty value is considered valid (optional field)
            return True, ""
            
        try:
            num_value = float(value)
            
            if min_value is not None and num_value < min_value:
                return False, f"Value must be at least {min_value}"
                
            if max_value is not None and num_value > max_value:
                return False, f"Value must be at most {max_value}"
                
            return True, ""
        except (ValueError, TypeError):
            return False, "Value must be a number"

# Usage examples:
# if not Validator.validate_email(email):
#     QMessageBox.warning(self, "Validation Error", "Invalid email format")
#     return
#
# is_valid, message = Validator.validate_required_field(name, "Name")
# if not is_valid:
#     QMessageBox.warning(self, "Validation Error", message)
#     return