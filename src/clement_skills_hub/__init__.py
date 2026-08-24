"""CLEMENT STUDIO Skills Hub.

The public API intentionally stays small: audit evidence is verified first,
then a deterministic import plan is built, materialized and validated.
"""

from .constants import GENERATOR_VERSION
from .extensions import effective_skill_entries, load_category_overrides, load_native_registry

__all__ = [
    "GENERATOR_VERSION",
    "effective_skill_entries",
    "load_category_overrides",
    "load_native_registry",
]
__version__ = GENERATOR_VERSION
