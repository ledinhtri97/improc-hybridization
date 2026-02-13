"""
VisualizeResults — Draw detections, crops, and masks onto the image.

This glue block visualizes the final pipeline output by:
  - Drawing bounding boxes on the original image
  - Overlaying SAM masks (if available)
  - Saving the result to a file

Input keys:
    image       : np.ndarray (H, W, 3) original BGR image
    boxes       : np.ndarray (K, 4) xyxy bounding boxes
    scores      : np.ndarray (K,) confidence scores
    classes     : np.ndarray (K,) class IDs

Optional input keys:
    masks       : list[np.ndarray] segmentation masks (from crops, not full image)

Output keys (added):
    output_path  : str path to the saved visualization
"""

from __future__ import annotations

import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from blocks.base import Block


class VisualizeResults(Block):
    """Draw boxes and masks, save visualization."""

    def __init__(
        self,
        output_path: str = "pipeline_result.jpg",
        show_labels: bool = True,
        show_scores: bool = True,
    ) -> None:
        """
        Args:
            output_path : File path to save the visualization.
            show_labels : Draw class IDs on boxes.
            show_scores : Draw confidence scores on boxes.
        """
        self.output_path = output_path
        self.show_labels = show_labels
        self.show_scores = show_scores
        if cv2 is None:
            raise ImportError("opencv-python is required for visualization")

    def __call__(self, data: dict) -> dict:
        image = data["image"].copy()
        boxes = data.get("boxes", np.array([]))
        scores = data.get("scores", np.array([]))
        classes = data.get("classes", np.array([]))
        masks = data.get("masks")

        # Draw bounding boxes first
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            # Choose color based on class (cycling through a palette)
            color = self._color_for_class(int(classes[i]) if len(classes) > i else 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), color.tolist(), 2)

            # Build label string
            label_parts = []
            if self.show_labels and len(classes) > i:
                label_parts.append(f"cls:{int(classes[i])}")
            if self.show_scores and len(scores) > i:
                label_parts.append(f"{scores[i]:.2f}")
            if label_parts:
                label = " ".join(label_parts)
                # Draw label background
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(image, (x1, y1 - th - 4), (x1 + tw, y1), color.tolist(), -1)
                cv2.putText(image, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw masks - each mask corresponds to a box/crop
        if masks is not None and len(masks) == len(boxes):
            for i, (box, mask) in enumerate(zip(boxes, masks)):
                x1, y1, x2, y2 = map(int, box)
                # Ensure mask fits the box region
                h_box = y2 - y1
                w_box = x2 - x1
                h_mask, w_mask = mask.shape[:2]

                # Resize mask if needed to match box dimensions
                if h_mask != h_box or w_mask != w_box:
                    mask_resized = cv2.resize(mask, (w_box, h_box), interpolation=cv2.INTER_NEAREST)
                else:
                    mask_resized = mask

                # Create colored overlay for this region
                color = self._color_for_class(int(classes[i]) if len(classes) > i else 0)
                mask_bool = mask_resized > 0
                colored_mask = np.zeros_like(image[y1:y2, x1:x2])
                colored_mask[mask_bool] = color.tolist()

                # Blend with original
                image[y1:y2, x1:x2] = cv2.addWeighted(
                    image[y1:y2, x1:x2], 0.6, colored_mask, 0.4, 0
                )

        # Save the result
        cv2.imwrite(self.output_path, image)

        return {
            **data,
            "output_path": self.output_path,
        }

    @staticmethod
    def _color_for_class(class_id: int) -> np.ndarray:
        """Generate a consistent color for each class ID."""
        colors = np.array([
            [255, 0, 0],    # blue
            [0, 255, 0],    # green
            [0, 0, 255],    # red
            [255, 255, 0],  # cyan
            [255, 0, 255],  # magenta
            [0, 255, 255],  # yellow
            [128, 0, 128],  # purple
            [255, 165, 0],  # orange
        ], dtype=np.uint8)
        return colors[class_id % len(colors)]
