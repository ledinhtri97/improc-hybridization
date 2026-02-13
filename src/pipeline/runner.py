"""
Pipeline — Sequential block executor.

Runs a fixed, ordered list of blocks where each block receives the
accumulated data dictionary from all previous blocks.  No DAG engine
or branching is required — a fixed but interleaved execution order
is sufficient per the architecture spec.
"""

from __future__ import annotations

import logging
import time
from typing import Sequence

import numpy as np

from blocks.base import Block

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Execute a sequence of blocks in order.

    Each block receives the full pipeline state dict and returns an
    updated dict.  The runner logs each step for inspectability.
    """

    def __init__(self, blocks: Sequence[Block]) -> None:
        self.blocks = list(blocks)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, data: dict) -> dict:
        """
        Run all blocks sequentially.

        Args:
            data: Initial pipeline state (must include at least "image").

        Returns:
            Final accumulated state dictionary.
        """
        logger.info(
            "Pipeline starting with %d block(s): %s",
            len(self.blocks),
            [b.name for b in self.blocks],
        )

        for i, block in enumerate(self.blocks, start=1):
            step_label = f"[{i}/{len(self.blocks)}] {block.name}"
            logger.info("%s — running", step_label)

            t0 = time.perf_counter()
            data = block(data)
            elapsed = time.perf_counter() - t0

            logger.info("%s — done (%.3fs)", step_label, elapsed)
            self._log_snapshot(data)

        logger.info("Pipeline complete.")
        return data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _log_snapshot(data: dict) -> None:
        """Log a brief summary of the current pipeline state."""
        summary_parts: list[str] = []
        for key, val in data.items():
            if isinstance(val, np.ndarray):
                summary_parts.append(f"{key}: ndarray{val.shape}")
            elif isinstance(val, list):
                summary_parts.append(f"{key}: list[{len(val)}]")
            elif isinstance(val, (int, float)):
                summary_parts.append(f"{key}: {val}")
            else:
                summary_parts.append(f"{key}: {type(val).__name__}")
        logger.debug("  state → {%s}", ", ".join(summary_parts))

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def describe(self) -> str:
        """Return a human-readable description of the pipeline."""
        lines = ["Hybrid Pipeline:"]
        for i, block in enumerate(self.blocks, start=1):
            lines.append(f"  {i}. {block.name}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        block_names = " → ".join(b.name for b in self.blocks)
        return f"Pipeline({block_names})"

    def __len__(self) -> int:
        return len(self.blocks)
