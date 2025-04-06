# models/patient_manager.py
import datetime
import copy
import json
import traceback

from PySide6.QtCore import QObject, Signal

class PatientManager(QObject):
    """
    Patient management system for medical clinic.
    Handles patient records, visit tracking, and medical history.
    """
    
    # Signals
    patient_added = Signal(str)  # patient_id
    patient_updated = Signal(str)  # patient_id
    patient_deleted = Signal(str)  # patient_id
    visit_started = Signal(str)   # patient_id
    visit_ended = Signal(str)     # patient_id
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger
        
        # Initialize from config or create new
        self.patients = self._initialize_patients()
        self.active_visits = self._initialize_visits()
    
    def _initialize_patients(self):
        """Initialize patient records from config or create new"""
        if "patients" in self.config_manager.config:
            return self.config_manager.config["patients"]
        else:
            self.config_manager.config["patients"] = {}
            return self.config_manager.config["patients"]
    
    def _initialize_visits(self):
        """Initialize active visits from config or create new"""
        if "active_visits" in self.config_manager.config:
            visits = self.config_manager.config["active_visits"]
            for patient_id, visit_data in visits.items():
                if "start_time" in visit_data and isinstance(visit_data["start_time"], str):
                    try:
                        visits[patient_id]["start_time"] = datetime.datetime.strptime(
                            visit_data["start_time"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        visits[patient_id]["start_time"] = datetime.datetime.now()
            return visits
        else:
            self.config_manager.config["active_visits"] = {}
            return self.config_manager.config["active_visits"]
    
    def save_data(self):
        """Save patient data to config"""
        # Make deep copy to avoid modifying original data
        patients_copy = copy.deepcopy(self.patients)
        visits_copy = copy.deepcopy(self.active_visits)
        
        # Convert datetime objects to strings for JSON serialization
        for patient_id, visit_data in visits_copy.items():
            if "start_time" in visit_data and isinstance(visit_data["start_time"], datetime.datetime):
                visit_data["start_time"] = visit_data["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to config
        self.config_manager.config["patients"] = patients_copy
        self.config_manager.config["active_visits"] = visits_copy
        return self.config_manager.save_config()
    
    def add_patient(self, patient_data):
        """Add a new patient record"""
        try:
            patient_id = patient_data.get("id", str(len(self.patients) + 1))
            
            if patient_id in self.patients:
                return False, f"Patient ID {patient_id} already exists"
            
            # Ensure required fields
            if not patient_data.get("name"):
                return False, "Patient name is required"
            
            # Add creation timestamp
            patient_data["created_on"] = datetime.datetime.now().isoformat()
            
            # Initialize medical history if not present
            if "medical_history" not in patient_data:
                patient_data["medical_history"] = []
            
            # Initialize visit history if not present
            if "visit_history" not in patient_data:
                patient_data["visit_history"] = []
            
            # Add to patients dictionary
            self.patients[patient_id] = patient_data
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.patient_added.emit(patient_id)
            
            return True, f"Patient {patient_data['name']} added successfully"
        except Exception as e:
            self.logger.error(f"Error adding patient: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def update_patient(self, patient_id, updated_data):
        """Update an existing patient record"""
        try:
            if patient_id not in self.patients:
                return False, f"Patient ID {patient_id} not found"
            
            # Get existing data
            patient = self.patients[patient_id]
            
            # Preserve history and visits
            medical_history = patient.get("medical_history", [])
            visit_history = patient.get("visit_history", [])
            created_on = patient.get("created_on")
            
            # Update with new data
            for key, value in updated_data.items():
                if key not in ["medical_history", "visit_history", "created_on"]:
                    patient[key] = value
            
            # Make sure histories are preserved
            patient["medical_history"] = medical_history
            patient["visit_history"] = visit_history
            patient["created_on"] = created_on
            
            # Add last updated timestamp
            patient["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.patient_updated.emit(patient_id)
            
            return True, f"Patient {patient['name']} updated successfully"
        except Exception as e:
            self.logger.error(f"Error updating patient: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def delete_patient(self, patient_id):
        """Delete a patient record"""
        try:
            if patient_id not in self.patients:
                return False, f"Patient ID {patient_id} not found"
            
            # Check if patient has an active visit
            if patient_id in self.active_visits:
                return False, f"Cannot delete patient with active visit. End the visit first."
            
            # Get patient name for confirmation message
            patient_name = self.patients[patient_id].get("name", "Unknown")
            
            # Remove patient
            del self.patients[patient_id]
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.patient_deleted.emit(patient_id)
            
            return True, f"Patient {patient_name} deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting patient: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def get_patient(self, patient_id):
        """Get a patient record by ID"""
        return self.patients.get(patient_id)
    
    def get_all_patients(self):
        """Get all patient records"""
        return self.patients
    
    def search_patients(self, search_term):
        """Search for patients by name, ID, or other fields"""
        search_term = search_term.lower()
        results = {}
        
        for patient_id, patient_data in self.patients.items():
            # Check various fields for the search term
            if (search_term in patient_id.lower() or
                search_term in patient_data.get("name", "").lower() or
                search_term in patient_data.get("phone", "").lower() or
                search_term in patient_data.get("email", "").lower()):
                results[patient_id] = patient_data
        
        return results
    
    def start_visit(self, patient_id, visit_data=None):
        """Start a new visit for a patient"""
        try:
            if patient_id not in self.patients:
                return False, f"Patient ID {patient_id} not found"
            
            # Check if patient already has an active visit
            if patient_id in self.active_visits:
                return False, f"Patient already has an active visit"
            
            # Initialize visit data
            if visit_data is None:
                visit_data = {}
            
            visit_data["start_time"] = datetime.datetime.now()
            visit_data["notes"] = visit_data.get("notes", "")
            visit_data["doctor"] = visit_data.get("doctor", "")
            visit_data["reason"] = visit_data.get("reason", "")
            visit_data["status"] = "active"
            
            # Add to active visits
            self.active_visits[patient_id] = visit_data
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.visit_started.emit(patient_id)
            
            return True, f"Visit started for patient {self.patients[patient_id]['name']}"
        except Exception as e:
            self.logger.error(f"Error starting visit: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def end_visit(self, patient_id, visit_notes=None):
        """End an active visit and add to visit history"""
        try:
            if patient_id not in self.patients:
                return False, f"Patient ID {patient_id} not found"
            
            if patient_id not in self.active_visits:
                return False, f"No active visit found for patient"
            
            # Get the active visit data
            visit_data = self.active_visits[patient_id]
            
            # Update with end time and notes
            visit_data["end_time"] = datetime.datetime.now().isoformat()
            
            if visit_notes:
                visit_data["notes"] = visit_notes.get("notes", visit_data.get("notes", ""))
                visit_data["diagnosis"] = visit_notes.get("diagnosis", "")
                visit_data["treatment"] = visit_notes.get("treatment", "")
                visit_data["follow_up"] = visit_notes.get("follow_up", "")
            
            visit_data["status"] = "completed"
            
            # Convert start_time to string if it's a datetime object
            if isinstance(visit_data["start_time"], datetime.datetime):
                visit_data["start_time"] = visit_data["start_time"].isoformat()
            
            # Add to patient's visit history
            self.patients[patient_id]["visit_history"].append(copy.deepcopy(visit_data))
            
            # Update medical history if diagnosis provided
            if visit_notes and "diagnosis" in visit_notes and visit_notes["diagnosis"]:
                medical_entry = {
                    "date": datetime.datetime.now().isoformat(),
                    "type": "diagnosis",
                    "condition": visit_notes["diagnosis"],
                    "notes": visit_notes.get("notes", ""),
                    "treatment": visit_notes.get("treatment", "")
                }
                self.patients[patient_id]["medical_history"].append(medical_entry)
            
            # Remove from active visits
            del self.active_visits[patient_id]
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.visit_ended.emit(patient_id)
            
            return True, f"Visit ended for patient {self.patients[patient_id]['name']}"
        except Exception as e:
            self.logger.error(f"Error ending visit: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def update_visit_notes(self, patient_id, notes):
        """Update notes for an active visit"""
        try:
            if patient_id not in self.active_visits:
                return False, "No active visit found"
            
            self.active_visits[patient_id]["notes"] = notes
            
            # Save changes
            self.save_data()
            
            return True, "Visit notes updated"
        except Exception as e:
            self.logger.error(f"Error updating visit notes: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def add_medical_history(self, patient_id, medical_data):
        """Add a medical history entry for a patient"""
        try:
            if patient_id not in self.patients:
                return False, f"Patient ID {patient_id} not found"
            
            # Check required fields
            if not medical_data.get("condition"):
                return False, "Medical condition is required"
            
            # Prepare medical history entry
            entry = {
                "date": datetime.datetime.now().isoformat(),
                "type": medical_data.get("type", "condition"),
                "condition": medical_data["condition"],
                "notes": medical_data.get("notes", ""),
                "treatment": medical_data.get("treatment", "")
            }
            
            # Add to patient's medical history
            if "medical_history" not in self.patients[patient_id]:
                self.patients[patient_id]["medical_history"] = []
                
            self.patients[patient_id]["medical_history"].append(entry)
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.patient_updated.emit(patient_id)
            
            return True, "Medical history added successfully"
        except Exception as e:
            self.logger.error(f"Error adding medical history: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def get_visit_history(self, patient_id):
        """Get full visit history for a patient"""
        if patient_id not in self.patients:
            return []
            
        return self.patients[patient_id].get("visit_history", [])
    
    def get_medical_history(self, patient_id):
        """Get full medical history for a patient"""
        if patient_id not in self.patients:
            return []
            
        return self.patients[patient_id].get("medical_history", [])
    
    def get_active_visit(self, patient_id):
        """Get active visit details for a patient if any"""
        return self.active_visits.get(patient_id)
    
    def get_all_active_visits(self):
        """Get all active visits"""
        active_visits = {}
        
        for patient_id, visit_data in self.active_visits.items():
            patient_name = self.patients.get(patient_id, {}).get("name", "Unknown")
            active_visits[patient_id] = {
                "patient_name": patient_name,
                "visit_data": visit_data
            }
        
        return active_visits