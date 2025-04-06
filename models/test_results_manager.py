# models/test_results_manager.py
import datetime
import copy
import json
import traceback
import uuid

from PySide6.QtCore import QObject, Signal

class TestResultsManager(QObject):
    """
    Medical test results management system.
    Handles tracking, storing, and retrieving patient test results.
    """
    
    # Signals
    result_added = Signal(str, str)  # patient_id, result_id
    result_updated = Signal(str, str)  # patient_id, result_id
    result_deleted = Signal(str, str)  # patient_id, result_id
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger
        
        # Initialize from config or create new
        self.test_results = self._initialize_test_results()
    
    def _initialize_test_results(self):
        """Initialize test results from config or create new"""
        if "test_results" in self.config_manager.config:
            return self.config_manager.config["test_results"]
        else:
            self.config_manager.config["test_results"] = {}
            return self.config_manager.config["test_results"]
    
    def save_data(self):
        """Save test results data to config"""
        # Make deep copy to avoid modifying original data
        results_copy = copy.deepcopy(self.test_results)
        
        # Save to config
        self.config_manager.config["test_results"] = results_copy
        return self.config_manager.save_config()
    
    def add_test_result(self, patient_id, result_data):
        """Add a new test result for a patient"""
        try:
            # Validate patient_id
            if not patient_id:
                return False, "Patient ID is required"
            
            # Generate unique ID if not provided
            result_id = result_data.get("id", str(uuid.uuid4()))
            
            # Initialize patient's test results if not exists
            if patient_id not in self.test_results:
                self.test_results[patient_id] = {}
            
            if result_id in self.test_results[patient_id]:
                return False, f"Test result ID {result_id} already exists for this patient"
            
            # Ensure required fields
            if not result_data.get("test_name"):
                return False, "Test name is required"
            
            if not result_data.get("test_date"):
                return False, "Test date is required"
            
            # Add creation timestamp
            result_data["created_on"] = datetime.datetime.now().isoformat()
            
            # Add to test results
            self.test_results[patient_id][result_id] = result_data
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.result_added.emit(patient_id, result_id)
            
            return True, f"Test result added successfully"
        except Exception as e:
            self.logger.error(f"Error adding test result: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def update_test_result(self, patient_id, result_id, updated_data):
        """Update an existing test result"""
        try:
            if patient_id not in self.test_results:
                return False, f"No test results found for patient ID {patient_id}"
            
            if result_id not in self.test_results[patient_id]:
                return False, f"Test result ID {result_id} not found"
            
            # Get existing data
            result = self.test_results[patient_id][result_id]
            
            # Update with new data
            for key, value in updated_data.items():
                result[key] = value
            
            # Add last updated timestamp
            result["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.result_updated.emit(patient_id, result_id)
            
            return True, f"Test result updated successfully"
        except Exception as e:
            self.logger.error(f"Error updating test result: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def delete_test_result(self, patient_id, result_id):
        """Delete a test result"""
        try:
            if patient_id not in self.test_results:
                return False, f"No test results found for patient ID {patient_id}"
            
            if result_id not in self.test_results[patient_id]:
                return False, f"Test result ID {result_id} not found"
            
            # Remove test result
            del self.test_results[patient_id][result_id]
            
            # If patient has no more test results, remove the patient entry
            if not self.test_results[patient_id]:
                del self.test_results[patient_id]
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.result_deleted.emit(patient_id, result_id)
            
            return True, f"Test result deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting test result: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def get_test_result(self, patient_id, result_id):
        """Get a specific test result by ID"""
        if patient_id not in self.test_results:
            return None
        
        return self.test_results[patient_id].get(result_id)
    
    def get_patient_test_results(self, patient_id):
        """Get all test results for a specific patient"""
        if patient_id not in self.test_results:
            return []
        
        # Convert dictionary to list of results with IDs
        results = []
        for result_id, result_data in self.test_results[patient_id].items():
            result_with_id = result_data.copy()
            result_with_id["id"] = result_id
            results.append(result_with_id)
        
        # Sort by test date (newest first)
        results.sort(key=lambda x: x.get("test_date", ""), reverse=True)
        
        return results
    
    def get_test_results_by_type(self, patient_id, test_type):
        """Get all test results of a specific type for a patient"""
        all_results = self.get_patient_test_results(patient_id)
        
        # Filter by test type
        return [result for result in all_results if result.get("test_name") == test_type]
    
    def get_test_results_in_range(self, patient_id, start_date, end_date):
        """Get all test results for a patient within a date range"""
        all_results = self.get_patient_test_results(patient_id)
        
        # Filter by date range
        filtered_results = []
        for result in all_results:
            test_date_str = result.get("test_date", "")
            if test_date_str:
                try:
                    test_date = datetime.datetime.fromisoformat(test_date_str).date()
                    if start_date <= test_date <= end_date:
                        filtered_results.append(result)
                except:
                    # Skip results with invalid dates
                    pass
        
        return filtered_results
    
    def get_test_types(self):
        """Get a list of all unique test types in the system"""
        test_types = set()
        
        for patient_results in self.test_results.values():
            for result_data in patient_results.values():
                test_type = result_data.get("test_name")
                if test_type:
                    test_types.add(test_type)
        
        return sorted(list(test_types))
    
    def get_numerical_test_results(self, patient_id, test_type):
        """Get all numerical test results of a specific type for trending"""
        test_results = self.get_test_results_by_type(patient_id, test_type)
        
        # Filter for results with numerical values
        numerical_results = []
        
        for result in test_results:
            value = result.get("value")
            if value is not None:
                try:
                    # Try to convert to float
                    numerical_value = float(value)
                    
                    # Create a data point with date and value
                    test_date = result.get("test_date", "")
                    if test_date:
                        try:
                            date_obj = datetime.datetime.fromisoformat(test_date)
                            numerical_results.append({
                                "date": date_obj,
                                "value": numerical_value,
                                "unit": result.get("unit", ""),
                                "reference_range": result.get("reference_range", ""),
                                "id": result.get("id", "")
                            })
                        except:
                            # Skip results with invalid dates
                            pass
                except:
                    # Skip non-numerical values
                    pass
        
        # Sort by date (oldest first for trend analysis)
        numerical_results.sort(key=lambda x: x["date"])
        
        return numerical_results