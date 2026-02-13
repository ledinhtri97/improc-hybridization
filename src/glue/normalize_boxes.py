"""
NormalizeBoxes — Normalize bounding box coordinates to [0, 1].

Converts absolute pixel coordinates to relative coordinates based on
image dimensions.  Useful when downstream blocks expect normalized
inputs.

Input keys:
    image : np.ndarray (H, W, 3)
    boxes : np.ndarray (K, 4) xyxy absolute pixel coords

Output keys (updated):
    boxes          : np.ndarray (K, 4) xyxy normalized to [0, 1]
    boxes_absolute : np.ndarray (K, 4) original absolute coords (preserved)
"""

from __future__ import annotations

import numpy as np

from blocks.base import Block


class NormalizeBoxes(Block):
    """Convert absolute pixel box coordinates to normalized [0, 1] range."""

    def __call__(self, data: dict) -> dict:
        image = data["image"]
        boxes = data["boxes"].copy()
        h, w = image.shape[:2]

        normalized = boxes.copy()
        normalized[:, [0, 2]] /= w  # x coordinates
        normalized[:, [1, 3]] /= h  # y coordinates

        return {
            **data,
            "boxes_absolute": boxes,
            "boxes": normalized,
        }
