"""
Folder Manager - Handles customer photo folder selection and photo loading
"""

import os
from typing import List, Optional
from pathlib import Path


class FolderManager:
    """Manages customer photo folder and photo loading operations"""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    
    def __init__(self):
        self.customer_folder_path: Optional[str] = None
        self.loaded_photos: List[str] = []
    
    def select_customer_folder(self) -> Optional[str]:
        """
        Opens macOS folder picker and returns selected folder path.
        Uses AppleScript for native macOS dialog.
        """
        import subprocess
        
        try:
            script = '''
            set theFolder to choose folder with prompt "Select Customer Photos Folder"
            return POSIX path of theFolder
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                folder_path = result.stdout.strip()
                self.customer_folder_path = folder_path
                self.load_photos()
                return folder_path
            else:
                return None
                
        except subprocess.TimeoutExpired:
            print("Folder selection timed out")
            return None
        except Exception as e:
            print(f"Error selecting folder: {e}")
            return None
    
    def load_photos(self) -> List[str]:
        """Loads all supported image files from customer folder"""
        if not self.customer_folder_path or not os.path.exists(self.customer_folder_path):
            self.loaded_photos = []
            return self.loaded_photos
        
        photos = []
        try:
            for filename in os.listdir(self.customer_folder_path):
                ext = Path(filename).suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(self.customer_folder_path, filename)
                    photos.append(full_path)
            
            photos.sort(key=lambda x: os.path.basename(x).lower())
            self.loaded_photos = photos
            
        except Exception as e:
            print(f"Error loading photos: {e}")
            self.loaded_photos = []
        
        return self.loaded_photos
    
    def get_photo_count(self) -> int:
        """Returns the number of loaded photos"""
        return len(self.loaded_photos)
    
    def get_sequential_photos(self, count: int) -> List[str]:
        """Returns first N photos in sequence (01, 02, 03...)"""
        if not self.loaded_photos:
            return []
        return self.loaded_photos[:min(count, len(self.loaded_photos))]
    
    def is_folder_loaded(self) -> bool:
        """Returns True if a customer folder is loaded"""
        return self.customer_folder_path is not None and len(self.loaded_photos) > 0