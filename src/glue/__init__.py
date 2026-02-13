"""
Lightweight adapter (glue) blocks.

Glue blocks follow the same Block interface but are responsible for
format conversion, coordinate transforms, cropping, and data reshaping
needed to connect blocks from different tools.
"""

from glue.crop_regions import CropRegions
from glue.box_to_point_prompt import BoxToPointPrompt
from glue.normalize_boxes import NormalizeBoxes
from glue.visualize import VisualizeResults

__all__ = ["CropRegions", "BoxToPointPrompt", "NormalizeBoxes", "VisualizeResults"]
