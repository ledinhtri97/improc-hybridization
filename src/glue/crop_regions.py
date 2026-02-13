"""
CropRegions — Crop image regions from bounding boxes.

Extracts sub-images from the original image for each bounding box.
This is glue between detection-phase blocks and per-region analysis
blocks (e.g., SAM segmentation, edge density scoring).

Input keys:
    image : np.ndarray (H, W, 3)
    boxes : np.ndarray (K, 4) xyxy format

Output keys (added):
    crops : list[np.ndarray]  — cropped image regions
"""

from __future__ import annotations

import numpy as np

from blocks.base import Block


class CropRegions(Block):
    """Crop image patches for each bounding box."""

    def __call__(self, data: dict) -> dict:
        image = data["image"]
        boxes = data["boxes"]
        crops: list[np.ndarray] = []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            # Clamp to image boundaries
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image.shape[1], x2)
            y2 = min(image.shape[0], y2)
            crops.append(image[y1:y2, x1:x2])

        return {
            **data,
            "crops": crops,
        }
