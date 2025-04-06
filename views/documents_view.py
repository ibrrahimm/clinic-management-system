# views/documents_view.py
import os
import datetime
import shutil
import subprocess
import platform
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QDialog, QFormLayout, QTextEdit,
                             QDateEdit, QComboBox, QMessageBox, QHeaderView,
                             QMenu, QFileDialog, QTabWidget, QListWidget,
                             QListWidgetItem, QFrame, QSplitter, QGridLayout,
                             QToolButton, QSizePolicy)
from PySide6.QtCore import Qt, QSize, QDate, Signal
from PySide6.QtGui import QIcon, QPixmap, QCursor


from models.patient_manager import PatientManager
from models.documents_manager import DocumentsManager

class DocumentEntryDialog(QDialog):
    """Dialog for entering or editing a document"""
    
    def __init__(self, config_manager, patient_id=None, document_data=None, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.patient_id = patient_id
        self.document_data = document_data or {}
        self.file_path = None  # Path to new file (if any)
        
        # Create documents manager
        self.documents_manager = DocumentsManager(config_manager)
        
        # Set dialog properties
        self.setWindowTitle("Document Information")
        self.setMinimumSize(500, 400)
        
        # Setup UI
        self._setup_ui()
        
        # Load documents if patient ID provided
        if patient_id:
            self.load_patient_documents()
    
    def _setup_ui(self):
        """Set up the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Header with patient info and controls
        header_layout = QHBoxLayout()
        
        self.patient_label = QLabel(f"Documents for: {self.patient_name}")
        self.patient_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.patient_label)
        
        # Add spacer
        header_layout.addStretch(1)
        
        # View toggle buttons
        view_layout = QHBoxLayout()
        
        # Table view button
        self.table_view_btn = QToolButton()
        self.table_view_btn.setText("Table")
        self.table_view_btn.setCheckable(True)
        self.table_view_btn.setChecked(True)
        self.table_view_btn.clicked.connect(lambda: self._set_view_mode("table"))
        view_layout.addWidget(self.table_view_btn)
        
        # Grid view button
        self.grid_view_btn = QToolButton()
        self.grid_view_btn.setText("Grid")
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.clicked.connect(lambda: self._set_view_mode("grid"))
        view_layout.addWidget(self.grid_view_btn)
        
        header_layout.addLayout(view_layout)
        
        # Add document button
        self.add_document_btn = QPushButton("Add Document")
        self.add_document_btn.clicked.connect(self._add_document)
        header_layout.addWidget(self.add_document_btn)
        
        # Import documents button
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self._import_documents)
        header_layout.addWidget(self.import_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search documents...")
        self.search_edit.textChanged.connect(self._filter_documents)
        search_layout.addWidget(self.search_edit)
        
        main_layout.addLayout(search_layout)
        
        # Split view with categories on left and documents on right
        splitter = QSplitter(Qt.Horizontal)
        
        # Categories list on left
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        
        categories_label = QLabel("Categories")
        categories_label.setStyleSheet("font-weight: bold;")
        categories_layout.addWidget(categories_label)
        
        self.categories_list = CategoryListWidget()
        self.categories_list.category_selected.connect(self._set_category_filter)
        categories_layout.addWidget(self.categories_list)
        
        splitter.addWidget(categories_widget)
        
        # Documents display on right (stacked widget for table/grid views)
        self.documents_widget = QTabWidget()
        self.documents_widget.setTabPosition(QTabWidget.South)
        self.documents_widget.setDocumentMode(True)
        self.documents_widget.tabBar().setVisible(False)  # Hide tab bar, we'll control via buttons
        
        # Table view tab
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        self.documents_table = DocumentsTable()
        self.documents_table.document_selected.connect(self._view_document)
        table_layout.addWidget(self.documents_table)
        
        self.documents_widget.addTab(table_tab, "Table")
        
        # Grid view tab
        grid_tab = QWidget()
        grid_layout = QVBoxLayout(grid_tab)
        
        self.grid_view = DocumentGridView()
        self.grid_view.document_selected.connect(self._view_document)
        grid_layout.addWidget(self.grid_view)
        
        self.documents_widget.addTab(grid_tab, "Grid")
        
        splitter.addWidget(self.documents_widget)
        
        # Set initial splitter sizes (30% categories, 70% documents)
        splitter.setSizes([3, 7])
        
        main_layout.addWidget(splitter, 1)  # 1 = stretch factor
        
        # Status bar
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
    
    def set_patient(self, patient_id):
        """Set the current patient and reload data"""
        self.patient_id = patient_id
        
        # Update patient name
        if patient_id:
            patient_data = self.patient_manager.get_patient(patient_id)
            if patient_data:
                self.patient_name = patient_data.get("name", "Unknown Patient")
                self.patient_label.setText(f"Documents for: {self.patient_name}")
        
        # Load documents
        self.load_patient_documents()
    
    def load_patient_documents(self):
        """Load all documents for the current patient"""
        if not self.patient_id:
            return
        
        # Get all documents
        all_documents = self.documents_manager.get_patient_documents(self.patient_id)
        
        # Update category list
        categories = set()
        for doc in all_documents:
            category = doc.get("category")
            if category:
                categories.add(category)
        
        self.categories_list.set_categories(categories)
        
        # Apply current filter if any
        self._apply_filters()
    
    def _set_view_mode(self, mode):
        """Switch between table and grid view modes"""
        if mode == "table":
            self.table_view_btn.setChecked(True)
            self.grid_view_btn.setChecked(False)
            self.documents_widget.setCurrentIndex(0)
            self.current_view = "table"
        else:  # grid
            self.table_view_btn.setChecked(False)
            self.grid_view_btn.setChecked(True)
            self.documents_widget.setCurrentIndex(1)
            self.current_view = "grid"
    
    def _set_category_filter(self, category):
        """Set the category filter and update the document display"""
        self.current_category = category
        self._apply_filters()
    
    def _filter_documents(self):
        """Filter documents based on search text"""
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply all current filters (search text and category) to documents"""
        if not self.patient_id:
            return
        
        search_text = self.search_edit.text().lower()
        
        # Get base document set (filtered by category if applicable)
        if self.current_category:
            documents = self.documents_manager.get_documents_by_category(
                self.patient_id, self.current_category)
        else:
            documents = self.documents_manager.get_patient_documents(self.patient_id)
        
        # Apply search filter if any
        if search_text:
            filtered_docs = []
            for doc in documents:
                # Search in name, category, description, source
                if (search_text in doc.get("name", "").lower() or
                    search_text in doc.get("category", "").lower() or
                    search_text in doc.get("description", "").lower() or
                    search_text in doc.get("source", "").lower()):
                    filtered_docs.append(doc)
            
            documents = filtered_docs
        
        # Update views
        self.documents_table.populate_documents(documents)
        self.grid_view.populate_documents(documents)
        
        # Update status
        self.status_label.setText(f"{len(documents)} documents")
    
    def _add_document(self):
        """Add a new document"""
        if not self.patient_id:
            QMessageBox.warning(self, "Error", "No patient selected")
            return
        
        dialog = DocumentEntryDialog(self.config_manager, self.patient_id, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get document data
            document_data = dialog.get_document_data()
            
            if document_data:
                # Add document
                success, message = self.documents_manager.add_document(
                    self.patient_id, document_data, dialog.file_path)
                
                if success:
                    self.status_label.setText("Document added successfully")
                    self.load_patient_documents()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add document: {message}")
    
    def _view_document(self, document_id):
        """View and manage a document"""
        if not self.patient_id:
            return
        
        # Get document data
        document_data = self.documents_manager.get_document(self.patient_id, document_id)
        
        if not document_data:
            QMessageBox.warning(self, "Error", "Document not found")
            return
        
        # Create a popup menu with options
        menu = QMenu(self)
        
        # Open option only available if there's a file
        if document_data.get("file_name"):
            open_action = QAction("Open Document", self)
            menu.addAction(open_action)
        
        view_action = QAction("View/Edit Details", self)
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Document", self)
        menu.addAction(delete_action)
        
        # Get the global cursor position
        global_pos = QCursor.pos()
        
        # Show menu at cursor position
        action = menu.exec_(global_pos)
        
        if action == open_action if 'open_action' in locals() else None:
            self._open_document(document_id)
        elif action == view_action:
            self._edit_document(document_id, document_data)
        elif action == delete_action:
            self._delete_document(document_id)
    
    def _open_document(self, document_id):
        """Open the document file with the default application"""
        # Get file path
        file_path = self.documents_manager.get_document_file_path(self.patient_id, document_id)
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "Document file not found")
            return
        
        try:
            # Open file with default application
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open document: {str(e)}")
    
    def _edit_document(self, document_id, document_data):
        """Edit document details"""
        # Create copy with ID included
        document_with_id = document_data.copy()
        document_with_id["id"] = document_id
        
        dialog = DocumentEntryDialog(
            self.config_manager, 
            self.patient_id,
            document_data=document_with_id, 
            parent=self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Get updated document data
            updated_data = dialog.get_document_data()
            
            if updated_data:
                # Update document
                success, message = self.documents_manager.update_document(
                    self.patient_id, document_id, updated_data, dialog.file_path)
                
                if success:
                    self.status_label.setText("Document updated successfully")
                    self.load_patient_documents()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update document: {message}")
    
    def _delete_document(self, document_id):
        """Delete a document"""
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this document? This will also delete the associated file.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.documents_manager.delete_document(
                self.patient_id, document_id)
            
            if success:
                self.status_label.setText("Document deleted")
                self.load_patient_documents()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete document: {message}")
    
    def _import_documents(self):
        """Import multiple documents"""
        if not self.patient_id:
            QMessageBox.warning(self, "Error", "No patient selected")
            return
        
        # Open file dialog for multiple files
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Documents to Import", "", "All Files (*.*)")
        
        if not file_paths:
            return  # User cancelled
        
        # Import each file
        success_count = 0
        
        for file_path in file_paths:
            # Create basic document data from file
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            
            # Remove extension from name
            base_name = os.path.splitext(file_name)[0]
            
            # Create document data
            document_data = {
                "name": base_name,
                "category": "Imported",
                "date": datetime.date.today().isoformat(),
                "description": f"Imported from {file_name}"
            }
            
            # Add document
            success, _ = self.documents_manager.add_document(
                self.patient_id, document_data, file_path)
            
            if success:
                success_count += 1
        
        # Reload documents
        self.load_patient_documents()
        
        # Show import summary
        QMessageBox.information(
            self, "Import Documents", 
            f"Successfully imported {success_count} of {len(file_paths)} documents.")
    
    def refresh(self):
        """Refresh the document display"""
        self.load_patient_documents()
        self._setup_ui()
        
        # Load document data if provided
        if document_data:
            self._load_document_data()
    
    def _setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Document name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter document name")
        form_layout.addRow("Document Name:", self.name_edit)
        
        # Document category
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        
        # Get existing categories
        categories = self.documents_manager.get_document_categories()
        self.category_combo.addItems(categories)
        
        # Add common categories if not already in the list
        common_categories = [
            "Insurance",
            "Medical Records",
            "Lab Results",
            "Prescriptions",
            "Consent Forms",
            "Identification",
            "Referrals",
            "Imaging",
            "Correspondence",
            "Billing"
        ]
        
        for category in common_categories:
            if category not in categories:
                self.category_combo.addItem(category)
        
        form_layout.addRow("Category:", self.category_combo)
        
        # Document date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Document Date:", self.date_edit)
        
        # Source
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Where the document came from")
        form_layout.addRow("Source:", self.source_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter description or notes about the document")
        form_layout.addRow("Description:", self.description_edit)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        form_layout.addRow("File:", file_layout)
        
        main_layout.addLayout(form_layout)
        
        # File information (shown only when editing)
        self.file_info_label = QLabel("")
        main_layout.addWidget(self.file_info_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _browse_file(self):
        """Browse for a file to attach"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document File", "", "All Files (*.*)")
        
        if file_path:
            self.file_path = file_path
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_str = self._format_file_size(file_size)
            
            self.file_label.setText(f"{file_name} ({size_str})")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _load_document_data(self):
        """Load document data into the form"""
        # Document name
        self.name_edit.setText(self.document_data.get("name", ""))
        
        # Category
        category = self.document_data.get("category", "")
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setCurrentText(category)
        
        # Document date
        date_str = self.document_data.get("date", "")
        if date_str:
            try:
                date_obj = datetime.datetime.fromisoformat(date_str).date()
                self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                # Use current date if parsing fails
                self.date_edit.setDate(QDate.currentDate())
        
        # Source
        self.source_edit.setText(self.document_data.get("source", ""))
        
        # Description
        self.description_edit.setText(self.document_data.get("description", ""))
        
        # File information
        file_name = self.document_data.get("file_name", "")
        file_size = self.document_data.get("file_size", 0)
        
        if file_name and file_size:
            size_str = self._format_file_size(file_size)
            file_ext = self.document_data.get("file_extension", "")
            
            self.file_info_label.setText(
                f"Current file: {file_name} ({size_str})\n"
                f"Type: {file_ext}")
    
    def get_document_data(self):
        """Get document data from the form"""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Document name is required.")
            return None
        
        category = self.category_combo.currentText().strip()
        if not category:
            QMessageBox.warning(self, "Input Error", "Category is required.")
            return None
        
        # Get document date
        document_date = self.date_edit.date().toString(Qt.ISODate)
        
        # Create document data dictionary
        document_data = {
            "name": name,
            "category": category,
            "date": document_date,
            "source": self.source_edit.text().strip(),
            "description": self.description_edit.toPlainText()
        }
        
        # If editing, preserve the ID and file info if no new file
        if "id" in self.document_data:
            document_data["id"] = self.document_data["id"]
            
            # Preserve file info if no new file selected
            if not self.file_path and "file_name" in self.document_data:
                document_data["file_name"] = self.document_data["file_name"]
                document_data["file_extension"] = self.document_data["file_extension"]
                document_data["file_size"] = self.document_data["file_size"]
        
        return document_data


class DocumentsTable(QTableWidget):
    """Custom table widget for displaying documents"""
    
    document_selected = Signal(str)  # Signal when a document is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up table properties
        self.setColumnCount(6)  # Name, Category, Date, Size, Source, Actions
        self.setHorizontalHeaderLabels(["Name", "Category", "Date", "Size", "Source", ""])
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Date
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Size
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Source
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        # Connect double-click signal
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
    
    def populate_documents(self, documents):
        """Populate table with documents"""
        # Clear existing data
        self.setRowCount(0)
        
        # Add documents to table
        for row, document in enumerate(documents):
            self.insertRow(row)
            
            # Name
            name = document.get("name", "Unknown")
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, document.get("id", ""))  # Store document ID
            self.setItem(row, 0, name_item)
            
            # Category
            category = document.get("category", "")
            category_item = QTableWidgetItem(category)
            self.setItem(row, 1, category_item)
            
            # Date
            date_str = document.get("date", "")
            if date_str:
                try:
                    date_obj = datetime.datetime.fromisoformat(date_str).date()
                    date_display = date_obj.strftime("%Y-%m-%d")
                except:
                    date_display = date_str
            else:
                date_display = ""
                
            date_item = QTableWidgetItem(date_display)
            self.setItem(row, 2, date_item)
            
            # Size
            file_size = document.get("file_size", 0)
            if file_size:
                size_str = self._format_file_size(file_size)
            else:
                size_str = "No file"
                
            size_item = QTableWidgetItem(size_str)
            self.setItem(row, 3, size_item)
            
            # Source
            source = document.get("source", "")
            source_item = QTableWidgetItem(source)
            self.setItem(row, 4, source_item)
            
            # Actions button
            view_btn = QPushButton("View")
            view_btn.setProperty("document_id", document.get("id", ""))
            view_btn.clicked.connect(self._on_view_clicked)
            self.setCellWidget(row, 5, view_btn)
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _on_cell_double_clicked(self, row, column):
        """Handle double-click on a table cell"""
        document_id = self.item(row, 0).data(Qt.UserRole)
        if document_id:
            self.document_selected.emit(document_id)
    
    def _on_view_clicked(self):
        """Handle view button click"""
        button = self.sender()
        if button:
            document_id = button.property("document_id")
            if document_id:
                self.document_selected.emit(document_id)


class CategoryListWidget(QListWidget):
    """Custom list widget for document categories"""
    
    category_selected = Signal(str)  # Signal when a category is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up list properties
        self.setSelectionMode(QListWidget.SingleSelection)
        
        # Add "All Documents" item
        self.addItem("All Documents")
        
        # Connect item clicked signal
        self.itemClicked.connect(self._on_item_clicked)
    
    def set_categories(self, categories):
        """Set the list of categories"""
        # Clear existing items (except "All Documents")
        while self.count() > 1:
            self.takeItem(1)
        
        # Add categories
        for category in sorted(categories):
            self.addItem(category)
    
    def _on_item_clicked(self, item):
        """Handle item click"""
        category = item.text()
        
        # Convert "All Documents" to empty string (no filter)
        if category == "All Documents":
            category = ""
            
        self.category_selected.emit(category)


class DocumentGridItem(QFrame):
    """Widget representing a document in grid view"""
    
    selected = Signal(str)  # Signal when the document is selected
    
    def __init__(self, document_data, parent=None):
        super().__init__(parent)
        
        self.document_data = document_data
        self.document_id = document_data.get("id", "")
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setFixedSize(150, 180)
        self.setStyleSheet("""
            DocumentGridItem {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            DocumentGridItem:hover {
                background-color: #f0f7ff;
                border-color: #4a86e8;
            }
        """)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Document icon (based on file extension)
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Get appropriate icon based on file extension
        file_ext = self.document_data.get("file_extension", "").lower()
        icon_pixmap = self._get_icon_for_extension(file_ext)
        
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)
        
        # Document name
        name_label = QLabel(self.document_data.get("name", "Unknown"))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)
        
        # Document category
        category_label = QLabel(self.document_data.get("category", ""))
        category_label.setAlignment(Qt.AlignCenter)
        category_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(category_label)
        
        # Date
        date_str = self.document_data.get("date", "")
        if date_str:
            try:
                date_obj = datetime.datetime.fromisoformat(date_str).date()
                date_display = date_obj.strftime("%Y-%m-%d")
            except:
                date_display = date_str
        else:
            date_display = ""
            
        date_label = QLabel(date_display)
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(date_label)
        
        # View button
        view_btn = QPushButton("View")
        view_btn.clicked.connect(self._on_view_clicked)
        layout.addWidget(view_btn)
    
    def _get_icon_for_extension(self, file_ext):
        """Get an appropriate icon for the file extension"""
        # Default icon size
        icon_size = QSize(64, 64)
        
        # Create blank pixmap
        pixmap = QPixmap(icon_size)
        pixmap.fill(Qt.transparent)
        
        # TODO: Replace with actual icons based on file type
        # For now, use a generic document icon
        
        return pixmap
    
    def _on_view_clicked(self):
        """Handle view button click"""
        self.selected.emit(self.document_id)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click event"""
        self.selected.emit(self.document_id)
        super().mouseDoubleClickEvent(event)


class DocumentGridView(QWidget):
    """Grid view for documents"""
    
    document_selected = Signal(str)  # Signal when a document is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components"""
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # This layout will be populated with DocumentGridItems
        
    def populate_documents(self, documents):
        """Populate grid with documents"""
        # Clear existing items
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add document items to grid
        for i, document in enumerate(documents):
            # Calculate row and column
            row = i // 4  # 4 items per row
            col = i % 4
            
            # Create document item
            doc_item = DocumentGridItem(document)
            doc_item.selected.connect(self.document_selected.emit)
            
            # Add to grid
            self.layout().addWidget(doc_item, row, col)
        
        # Add spacer to bottom-right to push items to top-left
        self.layout().addItem(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding, 
            self.layout().rowCount(), 
            self.layout().columnCount()
        )


class PatientDocumentsView(QWidget):
    """View for managing documents for a specific patient"""
    
    def __init__(self, config_manager, patient_id=None, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.patient_id = patient_id
        self.patient_name = "Unknown Patient"
        self.current_category = ""  # Current filter category (empty = all)
        self.current_view = "table"  # Current view mode (table or grid)
        
        # Create managers
        self.documents_manager = DocumentsManager(config_manager)
        self.patient_manager = PatientManager(config_manager)
        
        # Get patient name if ID provided
        if patient_id:
            patient_data = self.patient_manager.get_patient(patient_id)
            if patient_data:
                self.patient_name = patient_data.get("name", "Unknown Patient")
        
        # Setup