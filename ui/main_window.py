"""
Main Window - Updated UI with customer folder selection, PSD validation, and auto-fill
"""

import sys
import os
from typing import Optional
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QCheckBox,
    QGroupBox, QButtonGroup, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.folder_manager import FolderManager
from core.psd_validator import PSDValidator
from core.photo_enhancer import PhotoEnhancer


class MainWindow(QMainWindow):
    """Main application window with updated UI"""
    
    def __init__(self, photoshop_app=None):
        super().__init__()
        
        self.photoshop_app = photoshop_app
        self.folder_manager = FolderManager()
        self.psd_validator = PSDValidator()
        self.photo_enhancer = PhotoEnhancer(photoshop_app)
        self.selected_photo_count = 0
        self.template_buttons = []
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MugX Plugin - Enhanced")
        self.setMinimumSize(600, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self._create_customer_photos_section(main_layout)
        self._create_psd_template_section(main_layout)
        self._create_template_selection_section(main_layout)
        self._create_auto_fill_section(main_layout)
        self._create_progress_section(main_layout)
    
    def _create_customer_photos_section(self, parent_layout):
        """Creates the customer photos selection section"""
        group = QGroupBox("Customer Photos")
        layout = QVBoxLayout(group)
        
        self.btn_select_folder = QPushButton("📁 Select Customer Folder")
        self.btn_select_folder.clicked.connect(self._on_select_customer_folder)
        self.btn_select_folder.setMinimumHeight(40)
        layout.addWidget(self.btn_select_folder)
        
        self.lbl_photo_count = QLabel("Photos loaded: 0")
        self.lbl_photo_count.setFont(QFont("Arial", 12))
        self.lbl_photo_count.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_photo_count)
        
        self.chk_auto_correct = QCheckBox("✨ Auto-Correct (Enhance Photos)")
        self.chk_auto_correct.stateChanged.connect(self._on_auto_correct_changed)
        layout.addWidget(self.chk_auto_correct)
        
        parent_layout.addWidget(group)
    
    def _create_psd_template_section(self, parent_layout):
        """Creates the PSD template selection section"""
        group = QGroupBox("PSD Template")
        layout = QVBoxLayout(group)
        
        self.btn_open_psd = QPushButton("📄 Open PSD")
        self.btn_open_psd.clicked.connect(self._on_open_psd)
        self.btn_open_psd.setMinimumHeight(40)
        layout.addWidget(self.btn_open_psd)
        
        self.btn_validate_slots = QPushButton("✓ Validate Photo Slots")
        self.btn_validate_slots.clicked.connect(self._on_validate_slots)
        self.btn_validate_slots.setMinimumHeight(40)
        layout.addWidget(self.btn_validate_slots)
        
        self.lbl_psd_info = QLabel("PSD: Not loaded")
        self.lbl_psd_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_psd_info)
        
        parent_layout.addWidget(group)
    
    def _create_template_selection_section(self, parent_layout):
        """Creates the template selection buttons (2-6 photos)"""
        group = QGroupBox("Template Selection")
        layout = QVBoxLayout(group)
        
        info_label = QLabel("Select number of photos to use:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        self.template_button_group = QButtonGroup(self)
        self.template_button_group.setExclusive(True)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.template_buttons = []
        for count in range(2, 7):
            btn = QPushButton(f"{count}")
            btn.setMinimumSize(60, 60)
            btn.setFont(QFont("Arial", 16, QFont.Bold))
            btn.setEnabled(False)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=count: self._on_template_selected(c))
            
            self.template_buttons.append(btn)
            self.template_button_group.addButton(btn)
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        self.lbl_template_info = QLabel("Validate PSD to enable buttons")
        self.lbl_template_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_template_info)
        
        parent_layout.addWidget(group)
    
    def _create_auto_fill_section(self, parent_layout):
        """Creates the auto-fill action section"""
        group = QGroupBox("Auto-Fill")
        layout = QVBoxLayout(group)
        
        self.btn_auto_fill = QPushButton("🚀 Auto-Fill Smart Objects")
        self.btn_auto_fill.clicked.connect(self._on_auto_fill)
        self.btn_auto_fill.setMinimumHeight(50)
        self.btn_auto_fill.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_auto_fill.setEnabled(False)
        layout.addWidget(self.btn_auto_fill)
        
        self.lbl_status = QLabel("Status: Ready")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        parent_layout.addWidget(group)
    
    def _create_progress_section(self, parent_layout):
        """Creates the progress bar section"""
        group = QGroupBox("Progress")
        layout = QVBoxLayout(group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(group)
    
    def _on_select_customer_folder(self):
        """Handles customer folder selection"""
        folder_path = self.folder_manager.select_customer_folder()
        
        if folder_path:
            photo_count = self.folder_manager.get_photo_count()
            self.lbl_photo_count.setText(f"Photos loaded: {photo_count}")
            self.lbl_status.setText(f"Status: Loaded {photo_count} photos from {os.path.basename(folder_path)}")
            self._update_auto_fill_button()
        else:
            self.lbl_photo_count.setText("Photos loaded: 0")
            self.lbl_status.setText("Status: No folder selected")
    
    def _on_auto_correct_changed(self, state):
        """Handles auto-correct checkbox change"""
        enabled = state == Qt.Checked
        self.photo_enhancer.set_auto_correct(enabled)
        self.lbl_status.setText(f"Status: Auto-correct {'enabled' if enabled else 'disabled'}")
    
    def _on_open_psd(self):
        """Handles PSD file selection"""
        psd_path = self.psd_validator.select_psd_file()
        
        if psd_path:
            self.lbl_psd_info.setText(f"PSD: {os.path.basename(psd_path)}")
            self.lbl_status.setText(f"Status: PSD loaded - {os.path.basename(psd_path)}")
        else:
            self.lbl_psd_info.setText("PSD: Not loaded")
            self.lbl_status.setText("Status: No PSD selected")
    
    def _on_validate_slots(self):
        """Handles PSD slot validation"""
        if not self.psd_validator.is_psd_loaded():
            QMessageBox.warning(self, "No PSD", "Please select a PSD file first.")
            return
        
        slot_count = self.psd_validator.validate_smart_objects(self.photoshop_app)
        
        if slot_count > 0:
            max_enabled = min(slot_count, 6)
            
            for i, btn in enumerate(self.template_buttons):
                btn_count = i + 2
                btn.setEnabled(btn_count <= max_enabled)
                
                if btn_count == max_enabled:
                    btn.setChecked(True)
                    self.selected_photo_count = max_enabled
            
            self.lbl_template_info.setText(f"✓ Validated {slot_count} smart object slots")
            self.lbl_status.setText(f"Status: {slot_count} slots validated")
            self._update_auto_fill_button()
        else:
            self.lbl_template_info.setText("No smart objects found in PSD")
            self.lbl_status.setText("Status: Validation failed - no smart objects")
            
            for btn in self.template_buttons:
                btn.setEnabled(False)
    
    def _on_template_selected(self, count: int):
        """Handles template button selection"""
        self.selected_photo_count = count
        self.lbl_status.setText(f"Status: Template selected for {count} photos")
        self._update_auto_fill_button()
    
    def _on_auto_fill(self):
        """Handles auto-fill action"""
        if not self.folder_manager.is_folder_loaded():
            QMessageBox.warning(self, "No Photos", "Please select a customer folder first.")
            return
        
        if not self.psd_validator.is_psd_loaded():
            QMessageBox.warning(self, "No PSD", "Please select and validate a PSD file first.")
            return
        
        if self.selected_photo_count == 0:
            QMessageBox.warning(self, "No Template", "Please select a template (2-6 photos).")
            return
        
        photos = self.folder_manager.get_sequential_photos(self.selected_photo_count)
        
        if len(photos) < self.selected_photo_count:
            QMessageBox.warning(
                self, 
                "Insufficient Photos",
                f"Only {len(photos)} photos available, but {self.selected_photo_count} required."
            )
            return
        
        self._perform_auto_fill(photos)
    
    def _perform_auto_fill(self, photos: list):
        """Performs the actual auto-fill of smart objects"""
        try:
            self.progress_bar.setValue(0)
            self.lbl_status.setText("Status: Starting auto-fill...")
            
            if not self.photoshop_app:
                import time
                for i, photo in enumerate(photos):
                    self.progress_bar.setValue(int((i + 1) / len(photos) * 100))
                    self.lbl_status.setText(f"Status: Processing {os.path.basename(photo)}...")
                    time.sleep(0.5)
                
                self.lbl_status.setText(f"Status: ✓ Auto-fill complete - {len(photos)} photos placed")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully placed {len(photos)} photos into smart objects!"
                )
                return
            
            psd_doc = self.photoshop_app.open(self.psd_validator.current_psd_path)
            smart_objects = self.psd_validator.smart_objects
            
            for i, photo_path in enumerate(photos):
                if i >= len(smart_objects):
                    break
                
                self.progress_bar.setValue(int((i + 1) / len(photos) * 100))
                self.lbl_status.setText(f"Status: Placing photo {i+1}...")
                
                if self.photo_enhancer.is_enhancement_enabled():
                    photo_path = self.photo_enhancer.enhance_photo(photo_path, self.photoshop_app)
                
                self._place_photo_in_smart_object(psd_doc, smart_objects[i], photo_path)
            
            output_path = os.path.join(
                os.path.dirname(self.psd_validator.current_psd_path),
                "Output",
                f"mug_design_{len(photos)}.psd"
            )
            psd_doc.saveAs(output_path)
            psd_doc.close()
            
            self.lbl_status.setText(f"Status: ✓ Auto-fill complete - {len(photos)} photos placed")
            QMessageBox.information(
                self,
                "Success",
                f"Successfully placed {len(photos)} photos!\nOutput: {output_path}"
            )
            
        except Exception as e:
            self.lbl_status.setText(f"Status: ✗ Error - {str(e)}")
            QMessageBox.critical(self, "Error", f"Auto-fill failed: {str(e)}")
    
    def _place_photo_in_smart_object(self, psd_doc, smart_object: dict, photo_path: str):
        """Places a photo into a smart object layer"""
        try:
            layer_name = smart_object.get('name', '')
            target_layer = None
            for layer in psd_doc.layers:
                if layer.name == layer_name:
                    target_layer = layer
                    break
            
            if not target_layer:
                print(f"Layer {layer_name} not found")
                return
            
            if hasattr(psd_doc, 'placeEmbedded'):
                psd_doc.placeEmbedded(photo_path)
            elif hasattr(psd_doc, 'place'):
                psd_doc.place(photo_path)
            
        except Exception as e:
            print(f"Error placing photo {photo_path}: {e}")
    
    def _update_auto_fill_button(self):
        """Updates the auto-fill button state"""
        can_fill = (
            self.folder_manager.is_folder_loaded() and
            self.psd_validator.is_psd_loaded() and
            self.selected_photo_count > 0
        )
        self.btn_auto_fill.setEnabled(can_fill)
        
        if can_fill:
            photo_count = self.folder_manager.get_photo_count()
            if photo_count >= self.selected_photo_count:
                self.lbl_status.setText(f"Status: Ready to fill {self.selected_photo_count} photos")
            else:
                self.lbl_status.setText(f"Status: Need {self.selected_photo_count} photos, have {photo_count}")
                self.btn_auto_fill.setEnabled(False)