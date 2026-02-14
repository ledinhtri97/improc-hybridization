"""
API endpoints for block introspection.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException

from app.models import BlockSchema
from app.services.block_introspector import get_all_block_schemas, get_block_schema

router = APIRouter(prefix="/api/blocks", tags=["blocks"])


@router.get("", response_model=list[BlockSchema])
async def list_blocks():
    """Get all available blocks with their parameter schemas."""
    return get_all_block_schemas()


@router.get("/{block_id}", response_model=BlockSchema)
async def get_block(block_id: str):
    """Get schema for a specific block."""
    schema = get_block_schema(block_id)
    if schema is None:
        raise HTTPException(status_code=404, detail=f"Block not found: {block_id}")
    return schema
