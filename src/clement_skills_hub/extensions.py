"""Runtime overlay support for CLEMENT-native skills.

The certified import registry remains immutable evidence of the audited source
snapshot. Native skills and metadata corrections are layered on top to produce
an effective runtime view without falsifying the original audit metrics.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_native_registry(root: Path) -> dict[str, Any]:
    """Load the native extension registry."""
    return _load_json(root / "registry" / "native_skills_registry.json")


def load_category_overrides(root: Path) -> dict[str, dict[str, str]]:
    """Load metadata overrides keyed by canonical skill id."""
    payload = _load_json(root / "registry" / "category_overrides.json")
    overrides = payload.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("registry/category_overrides.json: overrides must be an object")
    return overrides


def effective_skill_entries(root: Path) -> list[dict[str, Any]]:
    """Return base + native skills with non-destructive metadata overrides applied."""
    base = _load_json(root / "registry" / "skills_registry.json")
    native = load_native_registry(root)
    overrides = load_category_overrides(root)

    base_entries = base.get("skills", [])
    native_entries = native.get("skills", [])
    if not isinstance(base_entries, list) or not isinstance(native_entries, list):
        raise ValueError("skill registries must expose a skills array")

    merged = [copy.deepcopy(entry) for entry in base_entries]
    merged.extend(copy.deepcopy(entry) for entry in native_entries)

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    seen_hashes: set[str] = set()
    for entry in merged:
        identifier = str(entry.get("id", ""))
        name = str(entry.get("name", "")).strip().lower()
        digest = str(entry.get("sha256", ""))
        if identifier in seen_ids:
            raise ValueError(f"duplicate skill id in effective registry: {identifier}")
        if name in seen_names:
            raise ValueError(f"duplicate skill name in effective registry: {name}")
        if digest in seen_hashes:
            raise ValueError(f"duplicate skill SHA256 in effective registry: {digest}")
        seen_ids.add(identifier)
        seen_names.add(name)
        seen_hashes.add(digest)

        patch = overrides.get(identifier)
        if patch:
            for key, value in patch.items():
                if key not in {"category"}:
                    raise ValueError(f"unsupported metadata override: {identifier}.{key}")
                entry[key] = value

    unknown_overrides = sorted(set(overrides) - seen_ids)
    if unknown_overrides:
        raise ValueError(f"category overrides reference unknown skills: {unknown_overrides}")

    return merged
