"""CLEMENT STUDIO Skills Hub.

The public API intentionally stays small: audit evidence is verified first,
then a deterministic import plan is built, materialized and validated.
"""

from .constants import GENERATOR_VERSION

__all__ = ["GENERATOR_VERSION"]
__version__ = GENERATOR_VERSION

