"""Auto-fill engine for placing photos into PSD template smart objects."""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class FillResult:
    """Result of auto-fill operation."""
    success: bool
    placed_count: int
    skipped_count: int
    errors: List[str]
    warnings: List[str]


@dataclass
class SmartObjectInfo:
    """Information about a smart object layer."""
    name: str
    index: int
    bounds: Optional[Tuple[int, int, int, int]]


class AutoFillEngine:
    """
    Engine for automatically filling photos into PSD template smart objects.
    
    This engine coordinates between the photo import service and Photoshop
    to place customer photos into design templates.
    """
    
    def __init__(self, photoshop_bridge=None):
        """
        Initialize the auto-fill engine.
        
        Args:
            photoshop_bridge: Bridge to Photoshop for executing ExtendScript commands.
        """
        self.photoshop_bridge = photoshop_bridge
        self.smart_object_pattern = re.compile(r'Photo[_\s]*(\d+)', re.IGNORECASE)
    
    def detect_smart_objects(self, psd_path: Path) -> List[SmartObjectInfo]:
        """Detect smart object layers in a PSD template."""
        return []
    
    def get_smart_object_name(self, index: int) -> str:
        """Get the standard smart object name for a given index."""
        return f"Photo_{index:02d}"
    
    def parse_smart_object_index(self, name: str) -> Optional[int]:
        """Parse the index from a smart object name."""
        match = self.smart_object_pattern.match(name)
        if match:
            return int(match.group(1))
        return None
    
    def prepare_fill_operation(
        self,
        photo_paths: List[Path],
        frame_count: int
    ) -> Tuple[List[Path], int, int]:
        """Prepare photos for filling into template frames."""
        photos_to_use = photo_paths[:frame_count]
        placed_count = len(photos_to_use)
        skipped_count = max(0, frame_count - len(photo_paths))
        
        return photos_to_use, placed_count, skipped_count
    
    def fill_template(
        self,
        psd_path: Path,
        photo_paths: List[Path],
        frame_count: int,
        smart_object_prefix: str = "Photo_"
    ) -> FillResult:
        """Fill a PSD template with photos."""
        errors = []
        warnings = []
        
        photos_to_use, placed_count, skipped_count = self.prepare_fill_operation(
            photo_paths, frame_count
        )
        
        if not photos_to_use:
            errors.append("No photos available to fill")
            return FillResult(
                success=False,
                placed_count=0,
                skipped_count=0,
                errors=errors,
                warnings=warnings
            )
        
        if self.photoshop_bridge:
            try:
                for idx, photo_path in enumerate(photos_to_use, start=1):
                    smart_object_name = f"{smart_object_prefix}{idx:02d}"
                    
                    success = self.photoshop_bridge.replace_smart_object(
                        smart_object_name,
                        str(photo_path)
                    )
                    
                    if not success:
                        errors.append(f"Failed to place {photo_path.name} in {smart_object_name}")
                        placed_count -= 1
                        
            except Exception as e:
                errors.append(f"Auto-fill error: {str(e)}")
                return FillResult(
                    success=False,
                    placed_count=0,
                    skipped_count=skipped_count,
                    errors=errors,
                    warnings=warnings
                )
        
        if skipped_count > 0:
            warnings.append(f"{skipped_count} frame(s) left empty - not enough photos")
        
        return FillResult(
            success=len(errors) == 0,
            placed_count=placed_count,
            skipped_count=skipped_count,
            errors=errors,
            warnings=warnings
        )
    
    def fill_template_sequential(
        self,
        psd_path: Path,
        photo_folder: Path,
        max_photos: int = 8
    ) -> FillResult:
        """Fill template with photos from folder in sequential order."""
        from .photo_import_service import PhotoImportService
        
        photo_service = PhotoImportService(str(photo_folder))
        photo_paths = photo_service.get_sequential_photos(max_photos)
        
        return self.fill_template(psd_path, photo_paths, max_photos)


class PhotoshopBridge:
    """Bridge to Photoshop for executing ExtendScript commands."""
    
    def __init__(self, cs_interface=None):
        """Initialize the Photoshop bridge."""
        self.cs_interface = cs_interface
    
    def replace_smart_object(
        self,
        smart_object_name: str,
        photo_path: str
    ) -> bool:
        """Replace contents of a smart object layer."""
        if not self.cs_interface:
            return False
        
        script = f"""
        (function() {{
            var doc = app.activeDocument;
            var layerName = "{smart_object_name}";
            var photoPath = "{photo_path}";
            
            try {{
                var layer = doc.layers.getByName(layerName);
                if (layer && layer.typename === 'ArtLayer' && layer.isSmartObject) {{
                    doc.activeLayer = layer;
                    var idPlacedLayer = charIDToTypeID( 'placedLayer' );
                    var desc = new ActionDescriptor();
                    var idPath = charIDToTypeID( 'Path' );
                    desc.putPath( idPath, new File( photoPath ) );
                    executeAction( idPlacedLayer, desc, DialogModes.NO );
                    return true;
                }}
                return false;
            }} catch (e) {{
                return false;
            }}
        }})();
        """
        
        try:
            result = self.cs_interface.evalScript(script)
            return result == "true"
        except Exception:
            return False
    
    def get_layer_bounds(self, layer_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get the bounds of a layer."""
        if not self.cs_interface:
            return None
        
        script = f"""
        (function() {{
            var doc = app.activeDocument;
            var layerName = "{layer_name}";
            
            try {{
                var layer = doc.layers.getByName(layerName);
                if (layer) {{
                    var bounds = layer.bounds;
                    return [bounds[0].value, bounds[1].value, bounds[2].value, bounds[3].value];
                }}
                return null;
            }} catch (e) {{
                return null;
            }}
        }})();
        """
        
        try:
            result = self.cs_interface.evalScript(script)
            if result and result != "null":
                import json
                return tuple(json.loads(result))
            return None
        except Exception:
            return None
