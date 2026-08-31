"""Photo Import Service with sequential naming and batch processing support."""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhotoFile:
    """Represents a photo file with sequential numbering."""
    path: Path
    original_name: str
    sequential_number: int
    extension: str


class PhotoImportService:
    """Service for importing and managing customer photos with sequential naming."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    def __init__(self, photo_folder: str = "D:/SublimationBag/Customer/Photo"):
        self.photo_folder = Path(photo_folder)
        self.ensure_folder_exists()
    
    def ensure_folder_exists(self):
        """Create photo folder if it doesn't exist."""
        self.photo_folder.mkdir(parents=True, exist_ok=True)
    
    def get_all_photos(self) -> List[Path]:
        """Get all supported photo files from the folder."""
        if not self.photo_folder.exists():
            return []
        
        photos = []
        for file in self.photo_folder.iterdir():
            if file.is_file() and file.suffix in self.SUPPORTED_EXTENSIONS:
                photos.append(file)
        
        return self._sort_photos_naturally(photos)
    
    def _sort_photos_naturally(self, photos: List[Path]) -> List[Path]:
        """Sort photos in natural order (01, 02, 03... not 1, 10, 2)."""
        def natural_sort_key(path: Path):
            name = path.stem
            # Try to extract numeric part
            match = re.match(r'^(\d+)', name)
            if match:
                return (0, int(match.group(1)), path.name)
            return (1, 0, path.name)
        
        return sorted(photos, key=natural_sort_key)
    
    def get_sequential_photos(self, count: int) -> List[Path]:
        """Get first N photos in sequential order."""
        all_photos = self.get_all_photos()
        return all_photos[:count]
    
    def get_next_sequential_number(self) -> int:
        """Get the next available sequential number for naming."""
        existing_numbers = set()
        
        for file in self.photo_folder.iterdir():
            if file.is_file() and file.suffix in self.SUPPORTED_EXTENSIONS:
                match = re.match(r'^(\d+)', file.stem)
                if match:
                    existing_numbers.add(int(match.group(1)))
        
        # Find first available number
        num = 1
        while num in existing_numbers:
            num += 1
        
        return num
    
    def auto_rename_photos(self, photo_paths: Optional[List[Path]] = None) -> List[PhotoFile]:
        """
        Rename photos to sequential numbers (01, 02, 03...).
        
        Args:
            photo_paths: List of photo paths to rename. If None, rename all photos.
        
        Returns:
            List of PhotoFile objects with new sequential names.
        """
        if photo_paths is None:
            photo_paths = self.get_all_photos()
        
        if not photo_paths:
            return []
        
        # First pass: collect all photos and assign temporary names
        temp_renames = []
        for idx, photo_path in enumerate(photo_paths, start=1):
            temp_name = f"_temp_{idx:04d}{photo_path.suffix}"
            temp_path = self.photo_folder / temp_name
            temp_renames.append((photo_path, temp_path, idx, photo_path.suffix))
        
        # Second pass: rename to temporary names
        for original, temp, idx, ext in temp_renames:
            if original.exists() and original != temp:
                try:
                    original.rename(temp)
                except Exception as e:
                    print(f"Warning: Could not rename {original}: {e}")
        
        # Third pass: rename to final sequential names
        renamed_photos = []
        for original, temp, idx, ext in temp_renames:
            final_name = f"{idx:02d}{ext}"
            final_path = self.photo_folder / final_name
            
            if temp.exists():
                try:
                    temp.rename(final_path)
                    renamed_photos.append(PhotoFile(
                        path=final_path,
                        original_name=original.name,
                        sequential_number=idx,
                        extension=ext
                    ))
                except Exception as e:
                    print(f"Warning: Could not rename {temp}: {e}")
        
        return renamed_photos
    
    def add_photos(self, new_photo_paths: List[Path]) -> List[PhotoFile]:
        """
        Add new photos to the folder and renumber all photos sequentially.
        
        Args:
            new_photo_paths: List of new photo paths to add.
        
        Returns:
            List of all photos after renumbering.
        """
        # Copy new photos to folder
        for new_photo in new_photo_paths:
            if new_photo.exists():
                dest = self.photo_folder / new_photo.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(new_photo, dest)
        
        # Renumber all photos
        return self.auto_rename_photos()
    
    def remove_photo(self, photo_path: Path) -> bool:
        """
        Remove a photo and renumber remaining photos.
        
        Args:
            photo_path: Path to photo to remove.
        
        Returns:
            True if successful, False otherwise.
        """
        if not photo_path.exists():
            return False
        
        try:
            photo_path.unlink()
            # Renumber remaining
            self.auto_rename_photos()
            return True
        except Exception as e:
            print(f"Error removing photo: {e}")
            return False
    
    def get_photo_count(self) -> int:
        """Get total number of photos in folder."""
        return len(self.get_all_photos())
    
    def validate_photos(self, photo_paths: List[Path]) -> Tuple[List[Path], List[str]]:
        """
        Validate that all photos exist and are supported formats.
        
        Returns:
            Tuple of (valid_photos, error_messages)
        """
        valid = []
        errors = []
        
        for path in photo_paths:
            if not path.exists():
                errors.append(f"Photo not found: {path}")
            elif path.suffix not in self.SUPPORTED_EXTENSIONS:
                errors.append(f"Unsupported format: {path.suffix}")
            else:
                valid.append(path)
        
        return valid, errors


class MobilePhotoImportService(PhotoImportService):
    """Photo import service for mobile cover photos."""
    
    def __init__(self, photo_folder: str = "D:/SublimationBag/Customer/Photo/Mobile"):
        super().__init__(photo_folder)
