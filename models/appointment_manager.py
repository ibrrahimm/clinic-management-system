# models/appointment_manager.py
import datetime
import copy
import json
import traceback
import uuid

from PySide6.QtCore import QObject, Signal, QDate

class AppointmentManager(QObject):
    """
    Appointment management system for medical clinic.
    Handles appointment scheduling, tracking, and management.
    """
    
    # Signals
    appointment_added = Signal(str)  # appointment_id
    appointment_updated = Signal(str)  # appointment_id
    appointment_deleted = Signal(str)  # appointment_id
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger
        
        # Initialize from config or create new
        self.appointments = self._initialize_appointments()
    
    def _initialize_appointments(self):
        """Initialize appointments from config or create new"""
        if "appointments" in self.config_manager.config:
            return self.config_manager.config["appointments"]
        else:
            self.config_manager.config["appointments"] = {}
            return self.config_manager.config["appointments"]
    
    def save_data(self):
        """Save appointment data to config"""
        # Make deep copy to avoid modifying original data
        appointments_copy = copy.deepcopy(self.appointments)
        
        # Save to config
        self.config_manager.config["appointments"] = appointments_copy
        return self.config_manager.save_config()
    
    def add_appointment(self, appointment_data):
        """Add a new appointment"""
        try:
            # Generate unique ID if not provided
            appointment_id = appointment_data.get("id", str(uuid.uuid4()))
            
            if appointment_id in self.appointments:
                return False, f"Appointment ID {appointment_id} already exists"
            
            # Ensure required fields
            if not appointment_data.get("patient_id"):
                return False, "Patient ID is required"
            
            if not appointment_data.get("datetime"):
                return False, "Appointment date and time is required"
            
            # Check for conflicting appointments
            if not self._check_appointment_available(appointment_data):
                return False, "Appointment time conflicts with an existing appointment"
            
            # Add creation timestamp
            appointment_data["created_on"] = datetime.datetime.now().isoformat()
            
            # Add status if not present
            if "status" not in appointment_data:
                appointment_data["status"] = "scheduled"
            
            # Add to appointments dictionary
            self.appointments[appointment_id] = appointment_data
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.appointment_added.emit(appointment_id)
            
            return True, f"Appointment scheduled successfully"
        except Exception as e:
            self.logger.error(f"Error adding appointment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def update_appointment(self, appointment_id, updated_data):
        """Update an existing appointment"""
        try:
            if appointment_id not in self.appointments:
                return False, f"Appointment ID {appointment_id} not found"
            
            # Get existing data
            appointment = self.appointments[appointment_id]
            
            # Check for conflicting appointments if date/time/doctor changed
            date_changed = (
                updated_data.get("datetime") is not None and 
                updated_data.get("datetime") != appointment.get("datetime")
            )
            
            doctor_changed = (
                updated_data.get("doctor") is not None and 
                updated_data.get("doctor") != appointment.get("doctor")
            )
            
            if date_changed or doctor_changed:
                # Create merged data for conflict check
                check_data = appointment.copy()
                check_data.update(updated_data)
                
                if not self._check_appointment_available(check_data, exclude_id=appointment_id):
                    return False, "Updated appointment time conflicts with an existing appointment"
            
            # Update data
            for key, value in updated_data.items():
                appointment[key] = value
            
            # Add last updated timestamp
            appointment["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.appointment_updated.emit(appointment_id)
            
            return True, f"Appointment updated successfully"
        except Exception as e:
            self.logger.error(f"Error updating appointment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment"""
        try:
            if appointment_id not in self.appointments:
                return False, f"Appointment ID {appointment_id} not found"
            
            # Remove appointment
            del self.appointments[appointment_id]
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.appointment_deleted.emit(appointment_id)
            
            return True, f"Appointment deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting appointment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def get_appointment(self, appointment_id):
        """Get an appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def get_all_appointments(self):
        """Get all appointments"""
        return self.appointments
    
    def get_patient_appointments(self, patient_id):
        """Get all appointments for a specific patient"""
        patient_appointments = []
        
        for appointment_id, appointment_data in self.appointments.items():
            if appointment_data.get("patient_id") == patient_id:
                # Add the appointment ID to the data
                appointment_with_id = appointment_data.copy()
                appointment_with_id["id"] = appointment_id
                patient_appointments.append(appointment_with_id)
        
        # Sort by date (ascending)
        patient_appointments.sort(key=lambda x: x.get("datetime", ""))
        
        return patient_appointments
    
    def get_doctor_appointments(self, doctor_name, start_date=None, end_date=None):
        """Get all appointments for a specific doctor"""
        doctor_appointments = []
        
        for appointment_id, appointment_data in self.appointments.items():
            if appointment_data.get("doctor") == doctor_name:
                # Filter by date range if provided
                if start_date or end_date:
                    appointment_date = None
                    try:
                        appointment_date = datetime.datetime.fromisoformat(appointment_data.get("datetime", ""))
                    except:
                        continue
                    
                    if start_date and appointment_date.date() < start_date:
                        continue
                    
                    if end_date and appointment_date.date() > end_date:
                        continue
                
                # Add the appointment ID to the data
                appointment_with_id = appointment_data.copy()
                appointment_with_id["id"] = appointment_id
                doctor_appointments.append(appointment_with_id)
        
        # Sort by date (ascending)
        doctor_appointments.sort(key=lambda x: x.get("datetime", ""))
        
        return doctor_appointments
    
    def get_appointments_for_date(self, date):
        """Get all appointments for a specific date"""
        date_appointments = []
        
        for appointment_id, appointment_data in self.appointments.items():
            try:
                appointment_datetime = datetime.datetime.fromisoformat(appointment_data.get("datetime", ""))
                appointment_date = appointment_datetime.date()
                
                # Convert QDate to Python date for comparison if needed
                if isinstance(date, QDate):
                    compare_date = datetime.date(date.year(), date.month(), date.day())
                else:
                    compare_date = date
                
                if appointment_date == compare_date:
                    # Add the appointment ID to the data
                    appointment_with_id = appointment_data.copy()
                    appointment_with_id["id"] = appointment_id
                    date_appointments.append(appointment_with_id)
            except:
                # Skip appointments with invalid dates
                continue
        
        # Sort by time
        date_appointments.sort(key=lambda x: x.get("datetime", ""))
        
        return date_appointments
    
    def get_appointments_in_range(self, start_date, end_date):
        """Get all appointments within a date range"""
        range_appointments = []
        
        for appointment_id, appointment_data in self.appointments.items():
            try:
                appointment_datetime = datetime.datetime.fromisoformat(appointment_data.get("datetime", ""))
                appointment_date = appointment_datetime.date()
                
                # Convert QDate to Python date for comparison if needed
                if isinstance(start_date, QDate):
                    start = datetime.date(start_date.year(), start_date.month(), start_date.day())
                else:
                    start = start_date
                
                if isinstance(end_date, QDate):
                    end = datetime.date(end_date.year(), end_date.month(), end_date.day())
                else:
                    end = end_date
                
                if start <= appointment_date <= end:
                    # Add the appointment ID to the data
                    appointment_with_id = appointment_data.copy()
                    appointment_with_id["id"] = appointment_id
                    range_appointments.append(appointment_with_id)
            except:
                # Skip appointments with invalid dates
                continue
        
        # Sort by date and time
        range_appointments.sort(key=lambda x: x.get("datetime", ""))
        
        return range_appointments
    
    def _check_appointment_available(self, appointment_data, exclude_id=None):
        """
        Check if the requested appointment time is available
        Returns True if available, False if conflicting
        """
        try:
            # Get appointment details
            datetime_str = appointment_data.get("datetime", "")
            doctor = appointment_data.get("doctor", "")
            duration = appointment_data.get("duration", 30)  # Default 30 minutes
            
            if not datetime_str or not doctor:
                return False
            
            # Parse datetime
            appointment_datetime = datetime.datetime.fromisoformat(datetime_str)
            
            # Calculate end time
            appointment_end = appointment_datetime + datetime.timedelta(minutes=duration)
            
            # Check for conflicts
            for appt_id, appt_data in self.appointments.items():
                # Skip the appointment we're updating
                if exclude_id and appt_id == exclude_id:
                    continue
                
                # Skip appointments with different doctors
                if appt_data.get("doctor") != doctor:
                    continue
                
                # Parse existing appointment time
                try:
                    existing_datetime = datetime.datetime.fromisoformat(appt_data.get("datetime", ""))
                    existing_duration = appt_data.get("duration", 30)
                    existing_end = existing_datetime + datetime.timedelta(minutes=existing_duration)
                    
                    # Check for overlap
                    if (appointment_datetime < existing_end and
                        appointment_end > existing_datetime):
                        return False  # Conflict found
                except:
                    # Skip if date parsing fails
                    continue
            
            return True  # No conflicts found
        except Exception as e:
            self.logger.error(f"Error checking appointment availability: {str(e)}")
            return False  # Error, assume not available
    
    def mark_appointment_completed(self, appointment_id, notes=None):
        """Mark an appointment as completed"""
        try:
            if appointment_id not in self.appointments:
                return False, f"Appointment ID {appointment_id} not found"
            
            # Update appointment status
            self.appointments[appointment_id]["status"] = "completed"
            self.appointments[appointment_id]["completed_on"] = datetime.datetime.now().isoformat()
            
            if notes:
                self.appointments[appointment_id]["notes"] = notes
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.appointment_updated.emit(appointment_id)
            
            return True, "Appointment marked as completed"
        except Exception as e:
            self.logger.error(f"Error marking appointment completed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def mark_appointment_cancelled(self, appointment_id, reason=None):
        """Mark an appointment as cancelled"""
        try:
            if appointment_id not in self.appointments:
                return False, f"Appointment ID {appointment_id} not found"
            
            # Update appointment status
            self.appointments[appointment_id]["status"] = "cancelled"
            self.appointments[appointment_id]["cancelled_on"] = datetime.datetime.now().isoformat()
            
            if reason:
                self.appointments[appointment_id]["cancel_reason"] = reason
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.appointment_updated.emit(appointment_id)
            
            return True, "Appointment cancelled"
        except Exception as e:
            self.logger.error(f"Error cancelling appointment: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"