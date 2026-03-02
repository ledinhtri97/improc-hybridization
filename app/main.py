"""
FastAPI main application.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import blocks, pipeline

# Create FastAPI app
app = FastAPI(
    title="Hybrid Pipeline API",
    description="API for the hybrid image processing pipeline",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (before any mounts)
app.include_router(blocks.router)
app.include_router(pipeline.router)

# Mount results directory for serving generated images
results_dir = Path(__file__).parent.parent / "src" / "results"
if results_dir.exists():
    app.mount("/results", StaticFiles(directory=str(results_dir)), name="results")


@app.get("/")
async def root():
    return {
        "message": "Hybrid Pipeline API",
        "docs": "/docs",
        "endpoints": {
            "blocks": "/api/blocks",
            "pipeline": "/api/pipeline/run",
            "upload": "/api/pipeline/upload"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
