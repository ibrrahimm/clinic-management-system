# models/documents_manager.py
import datetime
import copy
import json
import traceback
import uuid
import os
import shutil
from pathlib import Path

from PySide6.QtCore import QObject, Signal

class DocumentsManager(QObject):
    """
    Patient documents management system.
    Handles storing, categorizing, and retrieving patient documents.
    """
    
    # Signals
    document_added = Signal(str, str)  # patient_id, document_id
    document_updated = Signal(str, str)  # patient_id, document_id
    document_deleted = Signal(str, str)  # patient_id, document_id
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.logger = config_manager.logger
        
        # Initialize documents directory
        self.documents_dir = self._initialize_documents_dir()
        
        # Initialize from config or create new
        self.documents_metadata = self._initialize_documents_metadata()
    
    def _initialize_documents_dir(self):
        """Initialize and return the documents directory path"""
        # Create directory inside app data directory
        documents_dir = self.config_manager.app_data_dir / "patient_documents"
        documents_dir.mkdir(exist_ok=True)
        return documents_dir
    
    def _initialize_documents_metadata(self):
        """Initialize documents metadata from config or create new"""
        if "documents_metadata" in self.config_manager.config:
            return self.config_manager.config["documents_metadata"]
        else:
            self.config_manager.config["documents_metadata"] = {}
            return self.config_manager.config["documents_metadata"]
    
    def save_data(self):
        """Save documents metadata to config"""
        # Make deep copy to avoid modifying original data
        metadata_copy = copy.deepcopy(self.documents_metadata)
        
        # Save to config
        self.config_manager.config["documents_metadata"] = metadata_copy
        return self.config_manager.save_config()
    
    def get_patient_directory(self, patient_id):
        """Get the directory for a specific patient's documents"""
        patient_dir = self.documents_dir / patient_id
        patient_dir.mkdir(exist_ok=True)
        return patient_dir
    
    def add_document(self, patient_id, document_data, file_path=None):
        """Add a new document for a patient"""
        try:
            # Validate patient_id
            if not patient_id:
                return False, "Patient ID is required"
            
            # Generate unique ID if not provided
            document_id = document_data.get("id", str(uuid.uuid4()))
            
            # Initialize patient's documents metadata if not exists
            if patient_id not in self.documents_metadata:
                self.documents_metadata[patient_id] = {}
            
            if document_id in self.documents_metadata[patient_id]:
                return False, f"Document ID {document_id} already exists for this patient"
            
            # Ensure required fields
            if not document_data.get("name"):
                return False, "Document name is required"
            
            if not document_data.get("category"):
                return False, "Document category is required"
            
            # Add creation timestamp
            document_data["created_on"] = datetime.datetime.now().isoformat()
            
            # If file path is provided, copy file to patient directory
            if file_path:
                try:
                    # Get the file extension
                    file_ext = os.path.splitext(file_path)[1]
                    
                    # Create target file name
                    target_file_name = f"{document_id}{file_ext}"
                    
                    # Get patient directory
                    patient_dir = self.get_patient_directory(patient_id)
                    
                    # Create target file path
                    target_file_path = patient_dir / target_file_name
                    
                    # Copy file
                    shutil.copy2(file_path, target_file_path)
                    
                    # Update document data with file info
                    document_data["file_name"] = target_file_name
                    document_data["file_extension"] = file_ext
                    document_data["file_size"] = os.path.getsize(target_file_path)
                    
                except Exception as e:
                    self.logger.error(f"Error copying document file: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    return False, f"Error copying document file: {str(e)}"
            
            # Add to documents metadata
            self.documents_metadata[patient_id][document_id] = document_data
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.document_added.emit(patient_id, document_id)
            
            return True, f"Document added successfully"
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def update_document(self, patient_id, document_id, updated_data, new_file_path=None):
        """Update an existing document"""
        try:
            if patient_id not in self.documents_metadata:
                return False, f"No documents found for patient ID {patient_id}"
            
            if document_id not in self.documents_metadata[patient_id]:
                return False, f"Document ID {document_id} not found"
            
            # Get existing data
            document = self.documents_metadata[patient_id][document_id]
            
            # If a new file is provided, update the file
            if new_file_path:
                try:
                    # Get the file extension
                    file_ext = os.path.splitext(new_file_path)[1]
                    
                    # Create target file name
                    target_file_name = f"{document_id}{file_ext}"
                    
                    # Get patient directory
                    patient_dir = self.get_patient_directory(patient_id)
                    
                    # Create target file path
                    target_file_path = patient_dir / target_file_name
                    
                    # If there's an existing file with a different extension, remove it
                    old_file_name = document.get("file_name")
                    if old_file_name and old_file_name != target_file_name:
                        old_file_path = patient_dir / old_file_name
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # Copy new file
                    shutil.copy2(new_file_path, target_file_path)
                    
                    # Update document data with file info
                    updated_data["file_name"] = target_file_name
                    updated_data["file_extension"] = file_ext
                    updated_data["file_size"] = os.path.getsize(target_file_path)
                    
                except Exception as e:
                    self.logger.error(f"Error updating document file: {str(e)}")
                    self.logger.error(traceback.format_exc())
                    return False, f"Error updating document file: {str(e)}"
            
            # Update with new data
            for key, value in updated_data.items():
                document[key] = value
            
            # Add last updated timestamp
            document["last_updated"] = datetime.datetime.now().isoformat()
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.document_updated.emit(patient_id, document_id)
            
            return True, f"Document updated successfully"
        except Exception as e:
            self.logger.error(f"Error updating document: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def delete_document(self, patient_id, document_id):
        """Delete a document"""
        try:
            if patient_id not in self.documents_metadata:
                return False, f"No documents found for patient ID {patient_id}"
            
            if document_id not in self.documents_metadata[patient_id]:
                return False, f"Document ID {document_id} not found"
            
            # Get document data
            document = self.documents_metadata[patient_id][document_id]
            
            # If there's a file, delete it
            file_name = document.get("file_name")
            if file_name:
                patient_dir = self.get_patient_directory(patient_id)
                file_path = patient_dir / file_name
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove document metadata
            del self.documents_metadata[patient_id][document_id]
            
            # If patient has no more documents, remove the patient entry
            if not self.documents_metadata[patient_id]:
                del self.documents_metadata[patient_id]
            
            # Save changes
            self.save_data()
            
            # Emit signal
            self.document_deleted.emit(patient_id, document_id)
            
            return True, f"Document deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    def get_document(self, patient_id, document_id):
        """Get a specific document by ID"""
        if patient_id not in self.documents_metadata:
            return None
        
        return self.documents_metadata[patient_id].get(document_id)
    
    def get_document_file_path(self, patient_id, document_id):
        """Get the file path for a document"""
        document = self.get_document(patient_id, document_id)
        if not document:
            return None
        
        file_name = document.get("file_name")
        if not file_name:
            return None
        
        patient_dir = self.get_patient_directory(patient_id)
        return patient_dir / file_name
    
    def get_patient_documents(self, patient_id):
        """Get all documents for a specific patient"""
        if patient_id not in self.documents_metadata:
            return []
        
        # Convert dictionary to list of documents with IDs
        documents = []
        for doc_id, doc_data in self.documents_metadata[patient_id].items():
            doc_with_id = doc_data.copy()
            doc_with_id["id"] = doc_id
            documents.append(doc_with_id)
        
        # Sort by created date (newest first)
        documents.sort(key=lambda x: x.get("created_on", ""), reverse=True)
        
        return documents
    
    def get_documents_by_category(self, patient_id, category):
        """Get all documents of a specific category for a patient"""
        all_documents = self.get_patient_documents(patient_id)
        
        # Filter by category
        return [doc for doc in all_documents if doc.get("category") == category]
    
    def get_document_categories(self):
        """Get a list of all unique document categories in the system"""
        categories = set()
        
        for patient_docs in self.documents_metadata.values():
            for doc_data in patient_docs.values():
                category = doc_data.get("category")
                if category:
                    categories.add(category)
        
        return sorted(list(categories))