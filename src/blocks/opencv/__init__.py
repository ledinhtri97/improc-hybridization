"""OpenCV-derived rule-based geometric and image-processing blocks."""

from blocks.opencv.box_area_filter import BoxAreaFilter
from blocks.opencv.aspect_ratio_filter import AspectRatioFilter
from blocks.opencv.edge_density import EdgeDensityScorer

__all__ = ["BoxAreaFilter", "AspectRatioFilter", "EdgeDensityScorer"]
