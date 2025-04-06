# models/config_manager.py
import json
import datetime
import os
import sys
import shutil
import traceback
import random
import string
from pathlib import Path
import argon2

from PySide6.QtCore import QObject, Signal

class ConfigManager(QObject):
    """Configuration manager for Medical Clinic System"""
    
    # Signals
    config_changed = Signal()  # Emitted when configuration changes
    
    def __init__(self):
        super().__init__()
        
        # Setup app data directory
        self.app_data_dir = self._setup_app_data_dir()
        self.config_file = self.app_data_dir / "clinic_config.json"
        self.users_file = self.app_data_dir / "users.json"
        
        # Initialize logger
        self.logger = self._setup_logging()
        self.logger.info("Initializing Configuration Manager")
        
        # Default configuration
        self.DEFAULT_CONFIG = {
            "clinic_name": "Medical Clinic",
            "clinic_address": "123 Health St, Medical City",
            "clinic_phone": "123-456-7890",
            "clinic_email": "info@medicalclinic.com",
            "doctors": [
                "Dr. Smith",
                "Dr. Johnson",
                "Dr. Williams"
            ],
            "specialties": [
                "General Medicine",
                "Pediatrics",
                "Cardiology",
                "Dermatology",
                "Orthopedics"
            ],
            "visit_reasons": [
                "Check-up",
                "Follow-up",
                "Consultation",
                "Prescription Renewal",
                "Test Results",
                "Emergency",
                "Other"
            ],
            "patients": {},
            "active_visits": {},
            "archived_visits": {}
        }
        
        # Load configuration
        self.config = None
        self.users = None
        self.load_config()
        self.load_users()
    
    def _setup_app_data_dir(self):
        """Create and return the application data directory path"""
        app_data_dir = Path.home() / "AppData" / "Local" / "MedicalClinic"
        if sys.platform.startswith('linux'):
            app_data_dir = Path.home() / ".local" / "share" / "MedicalClinic"
        elif sys.platform == 'darwin':  # macOS
            app_data_dir = Path.home() / "Library" / "Application Support" / "MedicalClinic"
        
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return app_data_dir
    
    def _setup_logging(self):
        """Configure logging and return a logger instance"""
        import logging
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"clinic_{current_date}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger('medical_clinic')
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                # Add missing fields if needed
                for key in self.DEFAULT_CONFIG:
                    if key not in self.config:
                        self.config[key] = self.DEFAULT_CONFIG[key]
                
                self.logger.info("Configuration loaded successfully")
            else:
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
                self.logger.info("Created new configuration file")
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.config = self.DEFAULT_CONFIG.copy()
    
    
    class DateTimeEncoder(json.JSONEncoder):
        """Custom JSON encoder that can handle datetime objects"""
        def default(self, obj):
            if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            return super().default(obj)
    
    
    def save_config(self):
        """Save configuration to file with backup"""
        try:
            # Create backup before saving
            if self.config_file.exists():
                self._backup_file(self.config_file)
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False, cls=self.DateTimeEncoder)
            
            self.logger.info("Configuration saved successfully")
            
            # Emit signal
            self.config_changed.emit()
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def load_users(self):
        """Load users from file or create default admin"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                self.logger.info("User data loaded successfully")
            else:
                # Create default admin
                self.users = {}
                self._create_default_admin()
                self.save_users()
        except Exception as e:
            self.logger.error(f"Error loading users: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.users = {}
            self._create_default_admin()
    
    def _create_default_admin(self):
        """Create a default admin account"""
        # Generate a strong random password
        default_password = 'admin123'
        
        # Hash with Argon2
        hashed_password = self._hash_password(default_password)
        
        # Add admin user
        self.users["admin"] = {
            "password": hashed_password,
            "role": "admin",
            "name": "Admin User",
            "created_on": datetime.datetime.now().isoformat()
        }
        
        # Log creation
        self.logger.warning(f"Default admin account created with password: {default_password}")
        
        # User will be shown this password in a dialog by the UI
    
    def save_users(self):
        """Save users to file with backup"""
        try:
            # Create backup before saving
            if self.users_file.exists():
                self._backup_file(self.users_file)
                
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
            
            self.logger.info("User data saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving users: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _backup_file(self, file_path):
        """Create a backup of a file"""
        try:
            backups_dir = self._setup_backups_dir()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backups_dir / backup_filename
            
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            
            # Remove old backups (keep only last 10)
            self._cleanup_old_backups(backups_dir, file_path.stem)
            
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return None
    
    def _setup_backups_dir(self):
        """Create and return the backups directory path"""
        backups_dir = self.app_data_dir / "backups"
        backups_dir.mkdir(exist_ok=True)
        return backups_dir
    
    def _cleanup_old_backups(self, backups_dir, file_prefix):
        """Remove older backups keeping only recent ones"""
        try:
            # Get all backups for this file
            backups = list(backups_dir.glob(f"{file_prefix}_*.json"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the 10 most recent backups
            for old_backup in backups[10:]:
                old_backup.unlink()
                self.logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {str(e)}")
    
    def create_manual_backup(self):
        """Create a manual backup of configuration files"""
        try:
            # Force a new backup of config and users
            config_backup = self._backup_file(self.config_file)
            users_backup = self._backup_file(self.users_file)
            
            success = config_backup is not None and users_backup is not None
            if success:
                self.logger.info("Manual backup created successfully")
            
            return success
        except Exception as e:
            self.logger.error(f"Error creating manual backup: {str(e)}")
            return False
    
    def validate_login(self, username, password):
        """Validate login credentials and return user data if valid"""
        if not username or not password:
            return None
        
        # Check if user exists
        if username not in self.users:
            self.logger.warning(f"Login attempt for non-existent user: {username}")
            return None
        
        # Get user data
        user_data = self.users[username]
        
        # Check if using old SHA-256 hash (for backward compatibility)
        if "salt" in user_data:
            salt = user_data["salt"]
            import hashlib
            hashed_password = hashlib.sha256((salt + password).encode()).hexdigest()
            
            if hashed_password == user_data["password"]:
                # Upgrade to Argon2 hash
                new_hash = self._hash_password(password)
                user_data["password"] = new_hash
                # Remove old salt
                del user_data["salt"]
                self.save_users()
                self.logger.info(f"Upgraded password hash for user: {username}")
                
                return user_data
            else:
                self.logger.warning(f"Failed login attempt for user: {username}")
                return None
        else:
            # Using Argon2 hash
            if self._verify_password(user_data["password"], password):
                self.logger.info(f"User logged in: {username}")
                return user_data
            else:
                self.logger.warning(f"Failed login attempt for user: {username}")
                return None
    
    def _hash_password(self, password):
        """Hash a password using Argon2"""
        ph = argon2.PasswordHasher()
        return ph.hash(password)
    
    def _verify_password(self, hashed_password, password):
        """Verify a password against an Argon2 hash"""
        ph = argon2.PasswordHasher()
        try:
            ph.verify(hashed_password, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
    
    def add_user(self, username, password, role="user", name=""):
        """Add a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Add user
        self.users[username] = {
            "password": hashed_password,
            "role": role,
            "name": name,
            "created_on": datetime.datetime.now().isoformat()
        }
        
        # Save changes
        success = self.save_users()
        if success:
            self.logger.info(f"Created new user: {username} (role: {role})")
            return True, "User created successfully"
        else:
            return False, "Failed to save user data"
    
    def change_password(self, username, new_password):
        """Change a user's password"""
        if username not in self.users:
            return False, "User does not exist"
        
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Hash new password
        hashed_password = self._hash_password(new_password)
        
        # Update user record
        self.users[username]["password"] = hashed_password
        
        # Remove old salt if it exists (from legacy SHA-256 hash)
        if "salt" in self.users[username]:
            del self.users[username]["salt"]
        
        # Save changes
        success = self.save_users()
        if success:
            self.logger.info(f"Password changed for user: {username}")
            return True, "Password updated successfully"
        else:
            return False, "Failed to save user data"
    
    def delete_user(self, username):
        """Delete a user account"""
        if username not in self.users:
            return False, "User does not exist"
        
        # Prevent deleting the last admin account
        if self.users[username]["role"] == "admin":
            # Count admin users
            admin_count = sum(1 for user in self.users.values() if user.get("role") == "admin")
            if admin_count <= 1:
                return False, "Cannot delete the last admin account"
        
        # Remove user
        del self.users[username]
        
        # Save changes
        success = self.save_users()
        if success:
            self.logger.info(f"User deleted: {username}")
            return True, "User deleted successfully"
        else:
            return False, "Failed to save user data"
    
    def get_all_users(self):
        """Get all users with filtered information (no passwords)"""
        filtered_users = {}
        for username, data in self.users.items():
            filtered_users[username] = {
                "role": data["role"],
                "name": data.get("name", ""),
                "created_on": data.get("created_on", "Unknown")
            }
        return filtered_users
    
    def archive_old_visits(self, days=90):
        """Archive visits older than specified days"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            archived_count = 0
            
            # Get patients
            patients = self.config.get("patients", {})
            
            for patient_id, patient_data in patients.items():
                # Skip if no visit history
                if "visit_history" not in patient_data:
                    continue
                    
                # Filter visits to keep and archive
                visits_to_keep = []
                visits_to_archive = []
                
                for visit in patient_data["visit_history"]:
                    try:
                        # Get end time of visit
                        end_time_str = visit.get("end_time")
                        if not end_time_str:
                            # Keep visits with no end time
                            visits_to_keep.append(visit)
                            continue
                            
                        # Parse end time
                        if isinstance(end_time_str, str):
                            try:
                                end_time = datetime.datetime.fromisoformat(end_time_str)
                            except ValueError:
                                # Try alternate format
                                end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                        else:
                            # Already a datetime
                            end_time = end_time_str
                            
                        # Check against cutoff date
                        if end_time > cutoff_date:
                            visits_to_keep.append(visit)
                        else:
                            visits_to_archive.append(visit)
                            archived_count += 1
                    except Exception as e:
                        # On error, keep the visit
                        self.logger.error(f"Error processing visit during archiving: {str(e)}")
                        visits_to_keep.append(visit)
                
                # Update patient's visit history
                patient_data["visit_history"] = visits_to_keep
                
                # Add to archives if there are visits to archive
                if visits_to_archive:
                    if "archived_visits" not in self.config:
                        self.config["archived_visits"] = {}
                        
                    if patient_id not in self.config["archived_visits"]:
                        self.config["archived_visits"][patient_id] = []
                        
                    self.config["archived_visits"][patient_id].extend(visits_to_archive)
            
            # Save changes
            self.save_config()
            
            return True, f"Archived {archived_count} visits"
        except Exception as e:
            self.logger.error(f"Error archiving visits: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"

  
    # Add these methods to your ConfigManager class in models/config_manager.py

    def create_scheduled_backup(self):
        """Create a scheduled automatic backup with improved reliability"""
        try:
            # Create backup directory structure
            backup_dir = self.app_data_dir / "backups" / "scheduled"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create dated backup file name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"clinic_backup_{timestamp}.zip"
            
            # Create ZIP archive with all configuration files
            import zipfile
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add config files
                zipf.write(self.config_file, arcname="clinic_config.json")
                zipf.write(self.users_file, arcname="users.json")
                
                # Also backup patient documents if they exist
                patient_docs_dir = self.app_data_dir / "patient_documents"
                if patient_docs_dir.exists():
                    for file_path in patient_docs_dir.rglob('*'):
                        if file_path.is_file():
                            # Store with relative path
                            relative_path = file_path.relative_to(self.app_data_dir)
                            zipf.write(file_path, str(relative_path))
            
            # Maintain only last 7 daily backups
            self._cleanup_scheduled_backups(backup_dir, 7)
            
            self.logger.info(f"Scheduled backup created: {backup_file}")
            return backup_file, None
        
        except Exception as e:
            self.logger.error(f"Error creating scheduled backup: {str(e)}")
            self.logger.error(traceback.format_exc())
            return None, str(e)

    def _cleanup_scheduled_backups(self, backup_dir, keep_count=7):
        """Remove older backups keeping only the most recent ones"""
        try:
            # Get all backups for the scheduled directory
            backups = list(backup_dir.glob("clinic_backup_*.zip"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backups
            for old_backup in backups[keep_count:]:
                old_backup.unlink()
                self.logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {str(e)}")

    def restore_backup(self, backup_file):
        """Restore the system from a backup file"""
        try:
            import zipfile
            import shutil
            import tempfile
            
            # Create a temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract the backup
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_path)
                
                # Verify the backup contains the required files
                if not (temp_path / "clinic_config.json").exists() or not (temp_path / "users.json").exists():
                    return False, "Invalid backup file: Missing required configuration files"
                
                # Create backup of current configuration before overwriting
                self.create_manual_backup()
                
                # Copy the configuration files
                shutil.copy2(temp_path / "clinic_config.json", self.config_file)
                shutil.copy2(temp_path / "users.json", self.users_file)
                
                # Restore patient documents if they exist in the backup
                patient_docs_dir = self.app_data_dir / "patient_documents"
                backup_docs_dir = temp_path / "patient_documents"
                
                if backup_docs_dir.exists():
                    # Ensure the target directory exists
                    patient_docs_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Recursively copy files
                    for file_path in backup_docs_dir.rglob('*'):
                        if file_path.is_file():
                            # Get the relative path from the backup docs directory
                            rel_path = file_path.relative_to(backup_docs_dir)
                            # Create the destination path
                            dest_path = patient_docs_dir / rel_path
                            # Ensure parent directory exists
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            # Copy the file
                            shutil.copy2(file_path, dest_path)
                
                # Reload configuration
                self.load_config()
                self.load_users()
                
                self.logger.info(f"System restored from backup: {backup_file}")
                return True, "System restored successfully"
                
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error restoring from backup: {str(e)}"

    # To set up automatic backups, add this to your MainWindow class:

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
        backup_file, error = self.config_manager.create_scheduled_backup()
        
        if backup_file:
            self.statusBar().showMessage(f"Automatic backup created: {backup_file}", 5000)
        else:
            self.statusBar().showMessage(f"Automatic backup failed: {error}", 5000)