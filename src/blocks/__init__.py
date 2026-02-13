"""
Decomposed decision-unit blocks organized by tool origin.

Subpackages:
    yolo   — Blocks extracted from YOLOv8-nano workflow
    opencv — Rule-based geometric / image-processing blocks
    sam    — Blocks extracted from Segment Anything workflow
"""

from blocks.base import Block

from blocks.yolo.detect import YOLODetect
from blocks.yolo.confidence_filter import ConfidenceFilter
from blocks.yolo.class_filter import ClassFilter

from blocks.opencv.box_area_filter import BoxAreaFilter
from blocks.opencv.aspect_ratio_filter import AspectRatioFilter
from blocks.opencv.edge_density import EdgeDensityScorer

from blocks.sam.segment import SAMSegment

__all__ = [
    "Block",
    "YOLODetect",
    "ConfidenceFilter",
    "ClassFilter",
    "BoxAreaFilter",
    "AspectRatioFilter",
    "EdgeDensityScorer",
    "SAMSegment",
]
