"""
EdgeDensityScorer — OpenCV edge analysis on cropped regions.

Computes a simple edge-density metric for each crop using the Canny
edge detector.  This demonstrates that OpenCV-based analysis can be
applied *after* cropping — a post-crop decision block.

Input keys:
    crops : list[np.ndarray]  — cropped image regions

Output keys (added):
    edge_densities : list[float]  — edge density per crop (0.0–1.0)
"""

from __future__ import annotations

import cv2
import numpy as np

from blocks.base import Block


class EdgeDensityScorer(Block):
    """Compute Canny edge density for each cropped region."""

    def __init__(
        self,
        low_threshold: int = 50,
        high_threshold: int = 150,
    ) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def __call__(self, data: dict) -> dict:
        # Get crops - if not available, create from boxes
        crops = data.get("crops")
        if crops is None or len(crops) == 0:
            image = data["image"]
            boxes = data.get("boxes", [])
            crops = []
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                crops.append(image[y1:y2, x1:x2])
        
        densities: list[float] = []

        for crop in crops:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, self.low_threshold, self.high_threshold)
            total_pixels = edges.shape[0] * edges.shape[1]
            density = float(np.count_nonzero(edges) / total_pixels) if total_pixels > 0 else 0.0
            densities.append(density)

        return {
            **data,
            "edge_densities": densities,
        }
