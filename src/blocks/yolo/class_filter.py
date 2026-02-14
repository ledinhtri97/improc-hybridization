"""
ClassFilter — Class-based detection refilter.

Keeps only detections whose class ID is in an allowed set.  This can
appear *after* geometric filters from OpenCV, demonstrating that
YOLO-derived logic can be interleaved with other tool blocks.

Input keys:
    boxes   : np.ndarray (M, 4)
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


class ClassFilter(Block):
    """Keep only detections belonging to specified class IDs."""

    def __init__(self, allowed_classes) -> None:
        """
        Args:
            allowed_classes: Collection of integer class IDs to retain, or a single int.
        """
        # Handle single int or list of ints
        if isinstance(allowed_classes, int):
            self.allowed_classes = {allowed_classes}
        else:
            self.allowed_classes = set(allowed_classes)

    def __call__(self, data: dict) -> dict:
        classes = data["classes"]
        keep = np.array(
            [int(c) in self.allowed_classes for c in classes],
            dtype=bool,
        )

        return {
            **data,
            "boxes": data["boxes"][keep],
            "scores": data["scores"][keep],
            "classes": classes[keep],
        }
