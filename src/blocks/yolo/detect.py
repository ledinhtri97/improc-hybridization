"""
YOLODetect — Raw YOLO inference block.

Runs YOLOv8 model on the input image and exposes raw intermediate
outputs (bounding boxes, confidence scores, class IDs) as separate
arrays rather than an opaque result object.

Input keys:
    image : np.ndarray (H, W, 3) BGR image

Output keys (added):
    raw_boxes   : np.ndarray (N, 4) xyxy bounding boxes
    raw_scores  : np.ndarray (N,)   confidence scores
    raw_classes : np.ndarray (N,)   class IDs
"""

from __future__ import annotations

import numpy as np

from blocks.base import Block


class YOLODetect(Block):
    """Run YOLOv8 detection and expose raw intermediate outputs."""

    def __init__(self, model) -> None:
        """
        Args:
            model: A loaded ultralytics YOLO model instance.
        """
        self.model = model

    def __call__(self, data: dict) -> dict:
        image = data["image"]
        result = self.model(image)[0]

        return {
            **data,
            "raw_boxes": result.boxes.xyxy.cpu().numpy(),
            "raw_scores": result.boxes.conf.cpu().numpy(),
            "raw_classes": result.boxes.cls.cpu().numpy(),
        }
