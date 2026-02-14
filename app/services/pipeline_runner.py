"""
Pipeline runner service - dynamically executes blocks based on config.
"""

import sys
import uuid
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.models import BlockConfig, PipelineResult
from pipeline.runner import Pipeline


# Import all blocks
from blocks.yolo.detect import YOLODetect
from blocks.yolo.confidence_filter import ConfidenceFilter
from blocks.yolo.class_filter import ClassFilter
from blocks.opencv.box_area_filter import BoxAreaFilter
from blocks.opencv.aspect_ratio_filter import AspectRatioFilter
from blocks.opencv.edge_density import EdgeDensityScorer
from blocks.sam.segment import SAMSegment
from glue.crop_regions import CropRegions
from glue.box_to_point_prompt import BoxToPointPrompt
from glue.normalize_boxes import NormalizeBoxes
from glue.visualize import VisualizeResults


# Global model cache
_yolo_model = None
_sam_model = None


def get_yolo_model(model_name: str = "yolov8n.pt"):
    """Get or load YOLO model."""
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        _yolo_model = YOLO(model_name)
    return _yolo_model


def get_sam_model(model_name: str = "sam_b.pt"):
    """Get or load SAM model."""
    global _sam_model
    if _sam_model is None:
        from ultralytics import SAM
        _sam_model = SAM(model_name)
    return _sam_model


# Block class mapping - some need special handling
BLOCK_CLASSES = {
    "YOLODetect": YOLODetect,
    "ConfidenceFilter": ConfidenceFilter,
    "ClassFilter": ClassFilter,
    "BoxAreaFilter": BoxAreaFilter,
    "AspectRatioFilter": AspectRatioFilter,
    "EdgeDensityScorer": EdgeDensityScorer,
    "SAMSegment": SAMSegment,
    "CropRegions": CropRegions,
    "BoxToPointPrompt": BoxToPointPrompt,
    "NormalizeBoxes": NormalizeBoxes,
    "VisualizeResults": VisualizeResults,
}


def create_block(block_config: BlockConfig) -> Any:
    """
    Create a block instance from its configuration.
    """
    block_id = block_config.id
    params = block_config.params
    
    if block_id not in BLOCK_CLASSES:
        raise ValueError(f"Unknown block: {block_id}")
    
    block_class = BLOCK_CLASSES[block_id]
    
    # Handle special blocks that need loaded models
    if block_id == "YOLODetect":
        model_name = params.get("model", "yolov8n.pt")
        model = get_yolo_model(model_name)
        return block_class(model)
    
    if block_id == "SAMSegment":
        model_name = params.get("model", "sam_b.pt")
        model = get_sam_model(model_name)
        return block_class(model)
    
    # Get constructor parameters
    import inspect
    sig = inspect.signature(block_class.__init__)
    
    # Filter params to only include constructor parameters
    constructor_params = {}
    for param_name in sig.parameters:
        if param_name == "self":
            continue
        if param_name in params:
            constructor_params[param_name] = params[param_name]
    
    return block_class(**constructor_params)


def run_pipeline(blocks_config: list[BlockConfig], image: np.ndarray) -> PipelineResult:
    """
    Execute the pipeline with the given block configuration.
    """
    job_id = str(uuid.uuid4())
    
    try:
        # Create blocks from config
        blocks = []
        for block_config in blocks_config:
            block = create_block(block_config)
            blocks.append(block)
        
        # Create pipeline
        pipeline = Pipeline(blocks)
        
        # Run with block-level error tracking
        data = {"image": image}
        for i, block in enumerate(blocks):
            try:
                data = block(data)
            except Exception as block_error:
                raise RuntimeError(
                    f"Block {i+1}/{len(blocks)} failed: {block.name} - {str(block_error)}"
                ) from block_error
        
        result = data
        
        # Build response
        result_type = "text"
        result_data = {}
        
        # Check for text output
        text_parts = []
        if "boxes" in result and len(result.get("boxes", [])) > 0:
            n_boxes = len(result["boxes"])
            text_parts.append(f"Detections after filtering: {n_boxes}")
        
        if "scores" in result and len(result.get("scores", [])) > 0:
            scores = result["scores"]
            text_parts.append(f"Score range: {scores.min():.3f} - {scores.max():.3f}")
        
        if "classes" in result and len(result.get("classes", [])) > 0:
            classes = result["classes"]
            unique = np.unique(classes.astype(int))
            text_parts.append(f"Class IDs retained: {unique.tolist()}")
        
        if "masks" in result and result["masks"]:
            text_parts.append(f"Masks generated: {len(result['masks'])}")
        
        if text_parts:
            result_data["text"] = "\n".join(text_parts)
        
        # Check for image output (base64)
        if "output_base64" in result:
            result_type = "image"
            result_data["image_url"] = result["output_base64"]
        
        return PipelineResult(
            job_id=job_id,
            status="completed",
            type=result_type,
            data=result_data
        )
        
    except Exception as e:
        import traceback
        # Include pipeline info in error message
        try:
            pipeline_info = " → ".join([b.name for b in blocks])
        except:
            pipeline_info = "unknown"
        full_message = f"Pipeline: {pipeline_info}\n\nError: {str(e)}"
        return PipelineResult(
            job_id=job_id,
            status="failed",
            type="text",
            data={},
            message=full_message
        )
