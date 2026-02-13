#!/usr/bin/env python3
"""
run_pipeline.py — Runnable end-to-end hybrid pipeline demo.

Demonstrates non-sequential hybridization by interleaving blocks from
YOLOv8-nano, OpenCV, and SAM into a single pipeline that processes
one test image.

Pipeline order (interleaved, not tool-sequential):
  1. YOLODetect          [YOLO]    — raw detection
  2. ConfidenceFilter     [YOLO]    — score thresholding
  3. BoxAreaFilter        [OpenCV]  — geometric area filter
  4. AspectRatioFilter    [OpenCV]  — shape-based filter
  5. ClassFilter          [YOLO]    — class refilter (after OpenCV!)
  6. CropRegions          [Glue]    — crop image patches
  7. BoxToPointPrompt     [Glue]    — derive SAM prompts from boxes
  8. EdgeDensityScorer    [OpenCV]  — edge analysis on crops
  9. SAMSegment           [SAM]     — mask generation

Usage:
    python -m run_pipeline --image path/to/image.jpg
    python -m run_pipeline                            # uses built-in test image
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import cv2
import numpy as np

# ── Block imports ────────────────────────────────────────────────────
from blocks.yolo.detect import YOLODetect
from blocks.yolo.confidence_filter import ConfidenceFilter
from blocks.yolo.class_filter import ClassFilter
from blocks.opencv.box_area_filter import BoxAreaFilter
from blocks.opencv.aspect_ratio_filter import AspectRatioFilter
from blocks.opencv.edge_density import EdgeDensityScorer
from blocks.sam.segment import SAMSegment
from glue.crop_regions import CropRegions
from glue.box_to_point_prompt import BoxToPointPrompt
from glue.visualize import VisualizeResults
from pipeline.runner import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Model loaders ───────────────────────────────────────────────────

def load_yolo_model(model_name: str = "yolov8n.pt"):
    """Load YOLOv8-nano model."""
    from ultralytics import YOLO
    logger.info("Loading YOLO model: %s", model_name)
    return YOLO(model_name)


def load_sam_model(model_name: str = "sam_b.pt"):
    """Load SAM model via ultralytics."""
    from ultralytics import SAM
    logger.info("Loading SAM model: %s", model_name)
    return SAM(model_name)


def create_test_image() -> np.ndarray:
    """
    Create a simple synthetic test image with colored rectangles.

    This allows the pipeline to run without external image files or
    pretrained model weights for quick structural verification.
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200  # light gray bg

    # Draw some colored rectangles to simulate objects
    cv2.rectangle(img, (50, 50), (200, 180), (0, 0, 255), -1)     # red
    cv2.rectangle(img, (300, 100), (550, 350), (0, 255, 0), -1)    # green
    cv2.rectangle(img, (400, 20), (420, 40), (255, 0, 0), -1)      # blue (small)
    cv2.rectangle(img, (100, 300), (250, 460), (255, 255, 0), -1)  # cyan

    return img


# ── Pipeline construction ───────────────────────────────────────────

def build_hybrid_pipeline(
    yolo_model,
    sam_model,
    confidence_threshold: float = 0.4,
    min_box_area: float = 2000.0,
    allowed_classes: list[int] | None = None,
    output_path: str = "pipeline_result.jpg",
) -> Pipeline:
    """
    Construct the non-sequential hybrid pipeline.

    The block order is intentionally interleaved across tools:
      YOLO → YOLO → OpenCV → OpenCV → YOLO → Glue → Glue → OpenCV → SAM

    This is NOT:  Full YOLO → Full OpenCV → Full SAM
    """
    if allowed_classes is None:
        # COCO: 0=person, 2=car, 5=bus, 7=truck (example subset)
        allowed_classes = [0, 2, 5, 7]

    blocks = [
        # ── Detection phase (YOLO) ──────────────────────────────
        YOLODetect(yolo_model),             # [YOLO]   raw inference
        ConfidenceFilter(confidence_threshold),  # [YOLO]   score filter

        # ── Geometric filtering (OpenCV) ────────────────────────
        BoxAreaFilter(min_box_area),         # [OpenCV] area filter
        AspectRatioFilter(0.2, 5.0),         # [OpenCV] shape filter

        # ── Class refilter (YOLO-derived, after OpenCV!) ────────
        ClassFilter(allowed_classes),        # [YOLO]   interleaved!

        # ── Region preparation (Glue) ──────────────────────────
        CropRegions(),                       # [Glue]   crop patches
        BoxToPointPrompt(),                  # [Glue]   SAM prompts

        # ── Post-crop analysis (OpenCV) ─────────────────────────
        EdgeDensityScorer(),                 # [OpenCV] edge analysis

        # ── Segmentation (SAM) ──────────────────────────────────
        SAMSegment(sam_model),               # [SAM]    mask generation

        # ── Visualization (Glue) ────────────────────────────────
        VisualizeResults(output_path),       # [Glue]   save result
    ]

    return Pipeline(blocks)


# ── Result display ──────────────────────────────────────────────────

def print_results(data: dict) -> None:
    """Print a summary of the pipeline output."""
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS")
    print("=" * 60)

    n_boxes = len(data.get("boxes", []))
    print(f"  Detections after filtering : {n_boxes}")

    if "scores" in data and len(data["scores"]) > 0:
        print(f"  Score range               : {data['scores'].min():.3f} – {data['scores'].max():.3f}")

    if "classes" in data and len(data["classes"]) > 0:
        unique = np.unique(data["classes"].astype(int))
        print(f"  Class IDs retained        : {unique.tolist()}")

    if "crops" in data:
        print(f"  Crops generated           : {len(data['crops'])}")
        for i, crop in enumerate(data["crops"]):
            print(f"    crop[{i}] shape          : {crop.shape}")

    if "edge_densities" in data:
        print(f"  Edge densities            : {[f'{d:.3f}' for d in data['edge_densities']]}")

    if "masks" in data:
        print(f"  Masks generated           : {len(data['masks'])}")
        for i, mask in enumerate(data["masks"]):
            print(f"    mask[{i}] shape          : {mask.shape}")

    print("=" * 60)


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the hybrid image processing pipeline.",
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to input image.  Uses a synthetic test image if omitted.",
    )
    parser.add_argument(
        "--yolo-model",
        type=str,
        default="yolov8n.pt",
        help="YOLOv8 model name or path (default: yolov8n.pt).",
    )
    parser.add_argument(
        "--sam-model",
        type=str,
        default="sam_b.pt",
        help="SAM model name or path (default: sam_b.pt).",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.4,
        help="Confidence threshold (default: 0.4).",
    )
    parser.add_argument(
        "--min-area",
        type=float,
        default=2000.0,
        help="Minimum box area in pixels (default: 2000).",
    )
    args = parser.parse_args()

    # ── Load image ──────────────────────────────────────────────
    if args.image is not None:
        image_path = Path(args.image)
        if not image_path.exists():
            logger.error("Image not found: %s", image_path)
            sys.exit(1)
        image = cv2.imread(str(image_path))
        logger.info("Loaded image: %s (%s)", image_path, image.shape)
    else:
        image = create_test_image()
        logger.info("Using synthetic test image: %s", image.shape)

    # ── Load models ─────────────────────────────────────────────
    yolo_model = load_yolo_model(args.yolo_model)
    sam_model = load_sam_model(args.sam_model)

    # ── Build & run pipeline ────────────────────────────────────
    output_path = "results/pipeline_result.jpg"
    pipeline = build_hybrid_pipeline(
        yolo_model=yolo_model,
        sam_model=sam_model,
        confidence_threshold=args.confidence,
        min_box_area=args.min_area,
        output_path=output_path,
    )
    logger.info("\n%s", pipeline.describe())

    data = {"image": image}
    result = pipeline.run(data)

    # ── Show results ────────────────────────────────────────────
    print_results(result)


if __name__ == "__main__":
    main()
