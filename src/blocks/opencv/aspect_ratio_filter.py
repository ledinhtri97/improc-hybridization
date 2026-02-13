"""
AspectRatioFilter — Shape-based bounding box filter.

Removes boxes whose width/height aspect ratio falls outside an
acceptable range.  Useful for discarding degenerate (very thin/tall)
detections.

Input keys:
    boxes   : np.ndarray (M, 4) xyxy format
    scores  : np.ndarray (M,)
    classes : np.ndarray (M,)

Output keys (updated):
    boxes   : np.ndarray (K, 4)
    scores  : np.ndarray (K,)
    classes : np.ndarray (K,)
"""

from __future__ import annotations

import numpy as np

from blocks.base import Block


class AspectRatioFilter(Block):
    """Keep boxes whose aspect ratio is within [min_ratio, max_ratio]."""

    def __init__(
        self,
        min_ratio: float = 0.2,
        max_ratio: float = 5.0,
    ) -> None:
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

    def __call__(self, data: dict) -> dict:
        boxes = data["boxes"]
        widths = boxes[:, 2] - boxes[:, 0]
        heights = boxes[:, 3] - boxes[:, 1]

        # Avoid division by zero
        safe_heights = np.where(heights > 0, heights, 1.0)
        ratios = widths / safe_heights

        keep = (ratios >= self.min_ratio) & (ratios <= self.max_ratio)

        return {
            **data,
            "boxes": boxes[keep],
            "scores": data["scores"][keep],
            "classes": data["classes"][keep],
        }
