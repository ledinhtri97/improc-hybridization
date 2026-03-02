"""
API endpoints for pipeline execution.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

import httpx

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


@router.get("/fetch-image")
async def fetch_image(url: str):
    """
    Proxy endpoint to fetch an image from an external URL,
    avoiding CORS issues in the browser.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "image/jpeg")
        if not content_type.startswith("image/"):
            return JSONResponse(
                status_code=400,
                content={"detail": f"URL did not return an image (content-type: {content_type})"}
            )

        return Response(
            content=resp.content,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Remote server returned {e.response.status_code}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to fetch image: {e}"}
        )
