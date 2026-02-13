"""
ConfidenceFilter — Score-based detection filter.

Filters raw YOLO detections by a confidence threshold.  This isolates
the confidence-thresholding decision that is normally buried inside
YOLO's post-processing.

Input keys:
    raw_boxes   : np.ndarray (N, 4)
    raw_scores  : np.ndarray (N,)
    raw_classes : np.ndarray (N,)

Output keys (added/updated):
    boxes   : np.ndarray (M, 4)  — filtered boxes
    scores  : np.ndarray (M,)    — filtered scores
    classes : np.ndarray (M,)    — filtered class IDs
"""

from __future__ import annotations

from blocks.base import Block


class ConfidenceFilter(Block):
    """Keep only detections whose score exceeds a threshold."""

    def __init__(self, threshold: float = 0.4) -> None:
        self.threshold = threshold

    def __call__(self, data: dict) -> dict:
        keep = data["raw_scores"] > self.threshold

        return {
            **data,
            "boxes": data["raw_boxes"][keep],
            "scores": data["raw_scores"][keep],
            "classes": data["raw_classes"][keep],
        }
