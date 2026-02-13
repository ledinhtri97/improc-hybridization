"""
Abstract base class for all pipeline blocks.

Every block follows a strict contract:
  - Takes an explicit input dictionary
  - Returns an explicit output dictionary
  - No hidden state
  - No implicit mutation
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class Block(ABC):
    """Base interface for every decision block in the hybrid pipeline."""

    @abstractmethod
    def __call__(self, data: dict) -> dict:
        """
        Process data and return an updated dictionary.

        Args:
            data: Pipeline state dictionary. Must contain all keys
                  required by this block.

        Returns:
            A new dictionary with original keys preserved and
            block-specific keys added or updated.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Human-readable block identifier (defaults to class name)."""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.name}>"
