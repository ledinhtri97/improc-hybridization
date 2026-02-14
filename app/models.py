"""
Pydantic models for request/response schemas.
"""

from typing import Any
from pydantic import BaseModel


class BlockParameter(BaseModel):
    """Schema for a single block parameter."""
    name: str
    type: str  # "string", "number", "boolean", "array"
    default: Any = None
    required: bool = False
    description: str = ""


class BlockSchema(BaseModel):
    """Schema for a block returned by the API."""
    id: str
    name: str
    category: str  # "yolo", "opencv", "sam", "glue"
    description: str
    parameters: list[BlockParameter]


class BlockConfig(BaseModel):
    """Configuration for a single block in the pipeline."""
    id: str
    params: dict[str, Any] = {}


class PipelineRequest(BaseModel):
    """Request to execute a pipeline."""
    blocks: list[BlockConfig]
    image_id: str


class PipelineResult(BaseModel):
    """Result from pipeline execution."""
    job_id: str
    status: str  # "completed", "failed"
    type: str  # "text", "image", "both"
    data: dict[str, Any]
    message: str = ""


class ImageUploadResponse(BaseModel):
    """Response after image upload."""
    image_id: str
    filename: str
    size: int
