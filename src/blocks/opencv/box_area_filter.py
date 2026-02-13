"""
BoxAreaFilter — Geometric area-based filtering.

Uses OpenCV-style deterministic geometric logic to discard bounding boxes
whose pixel area falls below a minimum threshold.

Input keys:
    boxes   : np.ndarray (M, 4)  xyxy format
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


class BoxAreaFilter(Block):
    """Discard bounding boxes whose area is below *min_area* pixels."""

    def __init__(self, min_area: float = 2000.0) -> None:
        self.min_area = min_area

    def __call__(self, data: dict) -> dict:
        boxes = data["boxes"]
        widths = boxes[:, 2] - boxes[:, 0]
        heights = boxes[:, 3] - boxes[:, 1]
        areas = widths * heights
        keep = areas > self.min_area

        return {
            **data,
            "boxes": boxes[keep],
            "scores": data["scores"][keep],
            "classes": data["classes"][keep],
        }
