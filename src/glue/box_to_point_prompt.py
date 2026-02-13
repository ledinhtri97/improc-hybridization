"""
BoxToPointPrompt — Convert bounding box centers to SAM point prompts.

SAM can accept point prompts to guide segmentation.  This glue block
computes the center of each bounding box and formats it as a point
prompt relative to the corresponding crop.

Input keys:
    boxes : np.ndarray (K, 4) xyxy format

Output keys (added):
    point_prompts : list[np.ndarray]  — (1, 2) arrays, one per box
"""

from __future__ import annotations

import numpy as np

from blocks.base import Block


class BoxToPointPrompt(Block):
    """Derive SAM point prompts from bounding box centers."""

    def __call__(self, data: dict) -> dict:
        boxes = data["boxes"]
        prompts: list[np.ndarray] = []

        for box in boxes:
            x1, y1, x2, y2 = box
            # Center point relative to the crop (origin at top-left of box)
            cx = (x2 - x1) / 2.0
            cy = (y2 - y1) / 2.0
            prompts.append(np.array([[cx, cy]]))

        return {
            **data,
            "point_prompts": prompts,
        }
