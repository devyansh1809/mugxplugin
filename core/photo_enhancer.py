"""
Photo Enhancer - Auto-correct and enhance photos using Photoshop
"""

from typing import Optional, List
import os


class PhotoEnhancer:
    """Handles photo enhancement and auto-correction"""
    
    def __init__(self, photoshop_app=None):
        self.photoshop_app = photoshop_app
        self.auto_correct_enabled = False
    
    def set_auto_correct(self, enabled: bool):
        """Enables or disables auto-correct feature"""
        self.auto_correct_enabled = enabled
    
    def enhance_photo(self, photo_path: str, photoshop_doc=None) -> Optional[str]:
        """Enhances a single photo using Photoshop's auto-correct features"""
        if not self.auto_correct_enabled:
            return photo_path
        
        if not photoshop_doc or not self.photoshop_app:
            return photo_path
        
        try:
            doc = self.photoshop_app.open(photo_path)
            self._apply_auto_corrections(doc)
            doc.save()
            doc.close()
            return photo_path
            
        except Exception as e:
            print(f"Error enhancing photo {photo_path}: {e}")
            return photo_path
    
    def _apply_auto_corrections(self, photoshop_doc):
        """Applies Photoshop's built-in auto-corrections"""
        try:
            if hasattr(photoshop_doc, 'autoTone'):
                photoshop_doc.autoTone()
            elif hasattr(photoshop_doc, 'autoLevels'):
                photoshop_doc.autoLevels()
            
            if hasattr(photoshop_doc, 'autoContrast'):
                photoshop_doc.autoContrast()
            
            if hasattr(photoshop_doc, 'autoColor'):
                photoshop_doc.autoColor()
                
        except Exception as e:
            print(f"Error applying auto-corrections: {e}")
    
    def is_enhancement_enabled(self) -> bool:
        """Returns True if auto-enhancement is enabled"""
        return self.auto_correct_enabled