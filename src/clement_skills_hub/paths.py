"""Cross-platform path guards for the READ-ONLY source tree."""

from __future__ import annotations

import os
from pathlib import Path

from .errors import SourceIntegrityError


def resolved_descendant(root: Path, candidate: Path, *, require_file: bool = True) -> Path:
    """Resolve a candidate and reject traversal or symlink escape."""

    try:
        resolved_root = root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
    except OSError as exc:
        raise SourceIntegrityError(f"source path cannot be resolved: {candidate}: {exc}") from exc

    normalized_root = os.path.normcase(str(resolved_root))
    normalized_candidate = os.path.normcase(str(resolved_candidate))
    try:
        common = os.path.commonpath((normalized_root, normalized_candidate))
    except ValueError as exc:
        raise SourceIntegrityError(f"source path is on another volume: {candidate}") from exc

    if common != normalized_root or resolved_candidate == resolved_root:
        raise SourceIntegrityError(f"source path escapes certified root: {candidate}")
    if require_file and not resolved_candidate.is_file():
        raise SourceIntegrityError(f"source candidate is not a file: {candidate}")
    return resolved_candidate


def source_path(root: Path, raw_path: str) -> Path:
    if not raw_path:
        raise SourceIntegrityError("empty source path in audit inventory")
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    return resolved_descendant(root, candidate)


def relative_source_path(root: Path, candidate: Path) -> str:
    resolved_root = root.resolve(strict=True)
    resolved_candidate = resolved_descendant(root, candidate)
    return resolved_candidate.relative_to(resolved_root).as_posix()


def same_location(left: Path, right_text: str) -> bool:
    """Compare a runtime root with the immutable contract path."""

    return os.path.normcase(os.path.abspath(str(left))) == os.path.normcase(
        os.path.abspath(right_text)
    )

