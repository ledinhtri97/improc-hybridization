"""
API endpoints for pipeline execution.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.pipeline_runner import run_pipeline
from app.models import BlockConfig, PipelineResult

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run")
async def execute_pipeline(
    blocks: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Execute a pipeline with the given block configuration and image.
    
    The image is sent directly with the request - no separate upload needed.
    """
    # Parse blocks from JSON string
    try:
        blocks_data = json.loads(blocks)
        blocks_config = [BlockConfig(**b) for b in blocks_data]
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid JSON in blocks: {e}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid blocks config: {e}"}
        )
    
    # Read and decode image
    try:
        import cv2
        import numpy as np
        
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid image data - could not decode"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Failed to read image: {e}"}
        )
    
    # Run pipeline
    try:
        result = run_pipeline(blocks_config, img)
        return result
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Pipeline execution failed: {e}",
                "traceback": traceback.format_exc()
            }
        )
