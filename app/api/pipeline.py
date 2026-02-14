"""
API endpoints for pipeline execution.
"""

import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models import PipelineRequest, PipelineResult
from app.services.pipeline_runner import run_pipeline

# Store uploaded images in memory (for demo purposes)
# In production, use a proper storage solution
uploaded_images: dict[str, bytes] = {}

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineResult)
async def execute_pipeline(request: PipelineRequest):
    """
    Execute a pipeline with the given block configuration.
    """
    # Get the uploaded image
    if request.image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Decode image
    import cv2
    import numpy as np
    image_bytes = uploaded_images[request.image_id]
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image data")
    
    # Run pipeline
    result = run_pipeline(request.blocks, image)
    
    return result


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file.
    """
    contents = await file.read()
    image_id = str(uuid.uuid4())
    uploaded_images[image_id] = contents
    
    return {
        "image_id": image_id,
        "filename": file.filename,
        "size": len(contents)
    }
