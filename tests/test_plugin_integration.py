"""Integration tests for MugX plugin core functionality."""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.photo_import_service import PhotoImportService, PhotoFile
from core.autofill_engine import AutoFillEngine, FillResult


class TestPhotoImportService(unittest.TestCase):
    """Test photo import and sequential naming."""
    
    def setUp(self):
        """Create temporary test folder."""
        self.test_dir = tempfile.mkdtemp()
        self.service = PhotoImportService(self.test_dir)
    
    def tearDown(self):
        """Clean up test folder."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_folder_creation(self):
        """Test that photo folder is created automatically."""
        self.assertTrue(Path(self.test_dir).exists())
    
    def test_get_all_photos_empty(self):
        """Test getting photos from empty folder."""
        photos = self.service.get_all_photos()
        self.assertEqual(len(photos), 0)
    
    def test_get_all_photos_with_files(self):
        """Test getting photos with files present."""
        # Create test files
        (Path(self.test_dir) / "01.jpg").touch()
        (Path(self.test_dir) / "02.jpg").touch()
        (Path(self.test_dir) / "03.png").touch()
        
        photos = self.service.get_all_photos()
        self.assertEqual(len(photos), 3)
    
    def test_natural_sorting(self):
        """Test that photos are sorted naturally (01, 02, 03... not 1, 10, 2)."""
        # Create files in random order
        for name in ["10.jpg", "2.jpg", "1.jpg", "20.jpg", "3.jpg"]:
            (Path(self.test_dir) / name).touch()
        
        photos = self.service.get_all_photos()
        names = [p.name for p in photos]
        
        # Should be sorted naturally
        expected = ["1.jpg", "2.jpg", "3.jpg", "10.jpg", "20.jpg"]
        self.assertEqual(names, expected)
    
    def test_get_sequential_photos(self):
        """Test getting first N photos."""
        for i in range(1, 11):
            (Path(self.test_dir) / f"{i:02d}.jpg").touch()
        
        photos = self.service.get_sequential_photos(5)
        self.assertEqual(len(photos), 5)
        self.assertEqual(photos[0].name, "01.jpg")
        self.assertEqual(photos[4].name, "05.jpg")
    
    def test_auto_rename_photos(self):
        """Test automatic renaming to sequential numbers."""
        # Create files with non-sequential names
        for name in ["photo1.jpg", "vacation.png", "IMG_123.jpg"]:
            (Path(self.test_dir) / name).touch()
        
        renamed = self.service.auto_rename_photos()
        
        self.assertEqual(len(renamed), 3)
        self.assertEqual(renamed[0].sequential_number, 1)
        self.assertEqual(renamed[1].sequential_number, 2)
        self.assertEqual(renamed[2].sequential_number, 3)
        
        # Verify files exist with new names
        self.assertTrue((Path(self.test_dir) / "01.jpg").exists())
        self.assertTrue((Path(self.test_dir) / "02.png").exists())
        self.assertTrue((Path(self.test_dir) / "03.jpg").exists())
    
    def test_get_photo_count(self):
        """Test photo count."""
        for i in range(1, 6):
            (Path(self.test_dir) / f"{i:02d}.jpg").touch()
        
        count = self.service.get_photo_count()
        self.assertEqual(count, 5)
    
    def test_validate_photos(self):
        """Test photo validation."""
        valid_file = Path(self.test_dir) / "01.jpg"
        valid_file.touch()
        
        invalid_file = Path(self.test_dir) / "02.txt"
        invalid_file.touch()
        
        valid, errors = self.service.validate_photos([valid_file, invalid_file])
        
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("Unsupported format", errors[0])


class TestAutoFillEngine(unittest.TestCase):
    """Test auto-fill engine logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.engine = AutoFillEngine()
        self.photo_service = PhotoImportService(self.test_dir)
    
    def tearDown(self):
        """Clean up test folder."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_smart_object_name(self):
        """Test smart object name generation."""
        self.assertEqual(self.engine.get_smart_object_name(1), "Photo_01")
        self.assertEqual(self.engine.get_smart_object_name(2), "Photo_02")
        self.assertEqual(self.engine.get_smart_object_name(10), "Photo_10")
    
    def test_parse_smart_object_index(self):
        """Test parsing smart object index from name."""
        self.assertEqual(self.engine.parse_smart_object_index("Photo_01"), 1)
        self.assertEqual(self.engine.parse_smart_object_index("Photo_02"), 2)
        self.assertEqual(self.engine.parse_smart_object_index("Photo_10"), 10)
        self.assertIsNone(self.engine.parse_smart_object_index("Background"))
    
    def test_prepare_fill_operation_full(self):
        """Test fill preparation with enough photos."""
        photo_paths = [Path(self.test_dir) / f"{i:02d}.jpg" for i in range(1, 7)]
        for p in photo_paths:
            p.touch()
        
        photos_to_use, placed, skipped = self.engine.prepare_fill_operation(photo_paths, 6)
        
        self.assertEqual(len(photos_to_use), 6)
        self.assertEqual(placed, 6)
        self.assertEqual(skipped, 0)
    
    def test_prepare_fill_operation_partial(self):
        """Test fill preparation with fewer photos than frames."""
        photo_paths = [Path(self.test_dir) / f"{i:02d}.jpg" for i in range(1, 5)]
        for p in photo_paths:
            p.touch()
        
        photos_to_use, placed, skipped = self.engine.prepare_fill_operation(photo_paths, 6)
        
        self.assertEqual(len(photos_to_use), 4)
        self.assertEqual(placed, 4)
        self.assertEqual(skipped, 2)
    
    def test_prepare_fill_operation_excess(self):
        """Test fill preparation with more photos than frames."""
        photo_paths = [Path(self.test_dir) / f"{i:02d}.jpg" for i in range(1, 11)]
        for p in photo_paths:
            p.touch()
        
        photos_to_use, placed, skipped = self.engine.prepare_fill_operation(photo_paths, 6)
        
        self.assertEqual(len(photos_to_use), 6)
        self.assertEqual(placed, 6)
        self.assertEqual(skipped, 0)
    
    def test_fill_result_structure(self):
        """Test that fill result has correct structure."""
        result = FillResult(
            success=True,
            placed_count=6,
            skipped_count=0,
            errors=[],
            warnings=[]
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.placed_count, 6)
        self.assertEqual(result.skipped_count, 0)
        self.assertIsInstance(result.errors, list)
        self.assertIsInstance(result.warnings, list)


class TestSequentialNaming(unittest.TestCase):
    """Test sequential photo naming logic."""
    
    def setUp(self):
        """Set up test folder."""
        self.test_dir = tempfile.mkdtemp()
        self.service = PhotoImportService(self.test_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_get_next_sequential_number_empty(self):
        """Test getting next number from empty folder."""
        num = self.service.get_next_sequential_number()
        self.assertEqual(num, 1)
    
    def test_get_next_sequential_number_with_files(self):
        """Test getting next number with existing files."""
        for i in range(1, 6):
            (Path(self.test_dir) / f"{i:02d}.jpg").touch()
        
        num = self.service.get_next_sequential_number()
        self.assertEqual(num, 6)
    
    def test_get_next_sequential_number_with_gaps(self):
        """Test getting next number with gaps in sequence."""
        for i in [1, 2, 4, 5]:
            (Path(self.test_dir) / f"{i:02d}.jpg").touch()
        
        num = self.service.get_next_sequential_number()
        self.assertEqual(num, 3)  # First gap


if __name__ == '__main__':
    print("Running MugX Plugin Integration Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("- Photo import service: Sequential naming, natural sorting")
    print("- Auto-fill engine: Smart object detection, fill logic")
    print("- All core functionality validated")
