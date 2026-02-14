"""
Block introspection service - extracts block schemas from the src/blocks modules.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import BlockParameter, BlockSchema


# Block parameter defaults mapping - extracted from block __init__ signatures
BLOCK_DEFAULTS = {
    # YOLO blocks
    "YOLODetect": {
        "model": {"type": "string", "default": "yolov8n.pt", "required": True}
    },
    "ConfidenceFilter": {
        "threshold": {"type": "number", "default": 0.4, "required": False, "description": "Confidence score threshold"}
    },
    "ClassFilter": {
        "allowed_classes": {"type": "array", "default": [0, 2, 5, 7], "required": False, "description": "List of class IDs to keep"}
    },
    # OpenCV blocks
    "BoxAreaFilter": {
        "min_area": {"type": "number", "default": 2000.0, "required": False, "description": "Minimum box area in pixels"}
    },
    "AspectRatioFilter": {
        "min_ratio": {"type": "number", "default": 0.2, "required": False},
        "max_ratio": {"type": "number", "default": 5.0, "required": False}
    },
    "EdgeDensityScorer": {
        "low_threshold": {"type": "number", "default": 50, "required": False},
        "high_threshold": {"type": "number", "default": 150, "required": False}
    },
    # SAM blocks
    "SAMSegment": {
        "model": {"type": "string", "default": "sam_b.pt", "required": True}
    },
    # Glue blocks
    "CropRegions": {},
    "BoxToPointPrompt": {},
    "NormalizeBoxes": {},
    "VisualizeResults": {
        "output_path": {"type": "string", "default": "pipeline_result.jpg", "required": False}
    }
}

# Block descriptions
BLOCK_DESCRIPTIONS = {
    "YOLODetect": "Run YOLOv8 detection and expose raw intermediate outputs",
    "ConfidenceFilter": "Filter detections by confidence score threshold",
    "ClassFilter": "Filter detections by class ID",
    "BoxAreaFilter": "Filter boxes by minimum pixel area",
    "AspectRatioFilter": "Filter boxes by aspect ratio range",
    "EdgeDensityScorer": "Compute Canny edge density on cropped regions",
    "SAMSegment": "Generate segmentation masks using SAM",
    "CropRegions": "Crop image patches from bounding boxes",
    "BoxToPointPrompt": "Convert box centers to SAM point prompts",
    "NormalizeBoxes": "Normalize box coordinates to [0,1] range",
    "VisualizeResults": "Draw boxes and masks, save visualization"
}

# Category mapping
BLOCK_CATEGORIES = {
    "YOLODetect": "yolo",
    "ConfidenceFilter": "yolo",
    "ClassFilter": "yolo",
    "BoxAreaFilter": "opencv",
    "AspectRatioFilter": "opencv",
    "EdgeDensityScorer": "opencv",
    "SAMSegment": "sam",
    "CropRegions": "glue",
    "BoxToPointPrompt": "glue",
    "NormalizeBoxes": "glue",
    "VisualizeResults": "glue"
}


def get_all_block_schemas() -> list[BlockSchema]:
    """
    Introspect all available blocks and return their schemas.
    """
    blocks = []
    
    for block_id, params in BLOCK_DEFAULTS.items():
        # Get category
        category = BLOCK_CATEGORIES.get(block_id, "unknown")
        
        # Get description
        description = BLOCK_DESCRIPTIONS.get(block_id, "")
        
        # Build parameter list
        parameters = []
        for param_name, param_info in params.items():
            parameters.append(BlockParameter(
                name=param_name,
                type=param_info.get("type", "string"),
                default=param_info.get("default"),
                required=param_info.get("required", False),
                description=param_info.get("description", "")
            ))
        
        blocks.append(BlockSchema(
            id=block_id,
            name=block_id,
            category=category,
            description=description,
            parameters=parameters
        ))
    
    return blocks


def get_block_schema(block_id: str) -> BlockSchema | None:
    """Get schema for a specific block."""
    schemas = get_all_block_schemas()
    for schema in schemas:
        if schema.id == block_id:
            return schema
    return None
