"""Repository-wide structural and semantic validation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .constants import VALID_CATEGORIES, VALID_STATUSES
from .hashing import canonical_json, content_fingerprint, sha256_file
from .models import AuditContract, PlannedSkill
from .normalization import normalize_name
from .schema import load_json, validate_schema, validate_schema_document


REQUIRED_REPOSITORY_FILES = (
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "config/audit_contract.json",
    "registry/skills_registry.json",
    "schemas/skill.schema.json",
    "schemas/registry.schema.json",
    "docs/ARCHITECTURE.md",
    "docs/IMPORT_RUNBOOK.md",
    "docs/STATUS_POLICY.md",
    "docs/QA_REPORT.md",
)


def planned_content_fingerprint(skills: Iterable[PlannedSkill]) -> str:
    items: list[tuple[str, bytes]] = []
    for skill in skills:
        manifest = skill.manifest
        skill_path = str(manifest["content_path"])
        manifest_path = str(Path(skill_path).parent / "manifest.json").replace("\\", "/")
        items.append((skill_path, skill.content))
        items.append((manifest_path, canonical_json(manifest).encode("utf-8")))
    return content_fingerprint(items)


def skills_tree_fingerprint(skills_root: Path) -> str:
    items: list[tuple[str, bytes]] = []
    if skills_root.exists():
        for path in sorted(item for item in skills_root.rglob("*") if item.is_file()):
            if path.name not in {"SKILL.md", "manifest.json"}:
                continue
            relative = Path("skills") / path.relative_to(skills_root)
            items.append((relative.as_posix(), path.read_bytes()))
    return content_fingerprint(items)


def _cycle_nodes(entries: dict[str, dict[str, Any]]) -> set[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []
    cycle_members: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visited:
            return
        if identifier in visiting:
            start = path.index(identifier)
            cycle_members.update(path[start:])
            return
        visiting.add(identifier)
        path.append(identifier)
        for dependency in entries[identifier].get("dependencies", []):
            if dependency in entries:
                visit(dependency)
        path.pop()
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in sorted(entries):
        visit(identifier)
    return cycle_members


def validate_payload(
    skills_root: Path,
    registry: dict[str, Any],
    skill_schema: dict[str, Any],
    contract: AuditContract,
) -> list[str]:
    errors: list[str] = []
    entries_raw = registry.get("skills", [])
    if not isinstance(entries_raw, list):
        return ["registry.skills must be a list"]
    entries: dict[str, dict[str, Any]] = {}
    seen_names: set[str] = set()
    seen_hashes: set[str] = set()
    disk_manifest_paths: set[Path] = set()

    for index, entry in enumerate(entries_raw):
        if not isinstance(entry, dict):
            errors.append(f"registry skill #{index} is not an object")
            continue
        schema_errors = validate_schema(entry, skill_schema, path=f"$.skills[{index}]")
        errors.extend(schema_errors)
        identifier = str(entry.get("id", ""))
        normalized = normalize_name(str(entry.get("name", "")))
        digest = str(entry.get("sha256", ""))
        if identifier in entries:
            errors.append(f"duplicate skill id: {identifier}")
        entries[identifier] = entry
        if normalized in seen_names:
            errors.append(f"duplicate skill name: {normalized}")
        seen_names.add(normalized)
        if digest in seen_hashes:
            errors.append(f"duplicate skill SHA256: {digest}")
        seen_hashes.add(digest)

        content_path = str(entry.get("content_path", ""))
        if not content_path.startswith("skills/"):
            continue
        relative_under_skills = Path(*Path(content_path).parts[1:])
        skill_path = skills_root / relative_under_skills
        manifest_path = skill_path.parent / "manifest.json"
        disk_manifest_paths.add(manifest_path)
        if not skill_path.is_file():
            errors.append(f"missing normalized content: {content_path}")
        elif sha256_file(skill_path) != digest:
            errors.append(f"normalized SKILL.md SHA256 mismatch: {content_path}")
        if not manifest_path.is_file():
            errors.append(f"missing normalized manifest: {manifest_path}")
        else:
            try:
                disk_manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"invalid normalized manifest {manifest_path}: {exc}")
            else:
                if disk_manifest != entry:
                    errors.append(f"registry/manifest divergence: {identifier}")

    actual_manifests = set(skills_root.rglob("manifest.json")) if skills_root.exists() else set()
    unregistered = sorted(str(path) for path in actual_manifests - disk_manifest_paths)
    if unregistered:
        errors.append("unregistered manifests: " + ", ".join(unregistered[:10]))

    identifiers = set(entries)
    for identifier, entry in entries.items():
        dependencies = set(entry.get("dependencies", []))
        conflicts = set(entry.get("conflicts", []))
        missing_dependencies = dependencies - identifiers
        missing_conflicts = conflicts - identifiers
        if missing_dependencies:
            errors.append(f"{identifier}: missing dependencies {sorted(missing_dependencies)}")
        if missing_conflicts:
            errors.append(f"{identifier}: missing conflicts {sorted(missing_conflicts)}")
        if identifier in dependencies or identifier in conflicts:
            errors.append(f"{identifier}: self dependency/conflict")
        if dependencies & conflicts and entry.get("status") != "CONFLICT":
            errors.append(f"{identifier}: dependency/conflict overlap not marked CONFLICT")
        unresolved = list(entry.get("unresolved_dependencies", [])) + list(
            entry.get("unresolved_conflicts", [])
        )
        if unresolved and entry.get("status") in {"ACTIVE", "CANDIDATE"}:
            errors.append(f"{identifier}: unresolved references with status {entry.get('status')}")
        if entry.get("status") not in VALID_STATUSES:
            errors.append(f"{identifier}: invalid status")
        if entry.get("category") not in VALID_CATEGORIES:
            errors.append(f"{identifier}: invalid category")

    for identifier in _cycle_nodes(entries):
        if entries[identifier].get("status") != "CONFLICT":
            errors.append(f"{identifier}: dependency cycle not marked CONFLICT")

    state = registry.get("state")
    if state == "BOOTSTRAP":
        if entries:
            errors.append("BOOTSTRAP registry must be empty")
        if registry.get("content_fingerprint") is not None:
            errors.append("BOOTSTRAP content_fingerprint must be null")
    elif state in {"IMPORTED", "CERTIFIED"}:
        if len(entries) != contract.metrics.unique_by_sha256:
            errors.append(
                "imported entry count mismatch: "
                f"expected={contract.metrics.unique_by_sha256}, actual={len(entries)}"
            )
        actual_fingerprint = skills_tree_fingerprint(skills_root)
        if registry.get("content_fingerprint") != actual_fingerprint:
            errors.append(
                "content fingerprint mismatch: "
                f"expected={registry.get('content_fingerprint')}, actual={actual_fingerprint}"
            )
    else:
        errors.append(f"invalid registry state: {state!r}")

    expected_audit = contract.metrics.as_dict()
    if registry.get("audit") != expected_audit:
        errors.append("registry audit metrics differ from certified contract")
    if registry.get("source_snapshot_sha256") != contract.source_snapshot_sha256:
        errors.append("registry source snapshot differs from certified contract")

    statuses = Counter(str(entry.get("status")) for entry in entries.values())
    categories = Counter(str(entry.get("category")) for entry in entries.values())
    expected_stats = {
        "total_entries": len(entries),
        "by_status": dict(sorted(statuses.items())),
        "by_category": dict(sorted(categories.items())),
    }
    if registry.get("stats") != expected_stats:
        errors.append("registry stats mismatch")
    return errors


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_REPOSITORY_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    for category in VALID_CATEGORIES:
        if not (root / "skills" / category).is_dir():
            errors.append(f"missing category directory: skills/{category}")
    if errors:
        return errors

    try:
        contract = AuditContract.load(root / "config" / "audit_contract.json")
        skill_schema = load_json(root / "schemas" / "skill.schema.json")
        registry_schema = load_json(root / "schemas" / "registry.schema.json")
        registry = load_json(root / "registry" / "skills_registry.json")
    except Exception as exc:
        return [str(exc)]

    for name, schema in (("skill", skill_schema), ("registry", registry_schema)):
        document_errors = validate_schema_document(schema)
        errors.extend(f"{name} schema: {error}" for error in document_errors)
    errors.extend(validate_schema(registry, registry_schema, path="$registry"))
    errors.extend(validate_payload(root / "skills", registry, skill_schema, contract))
    return errors
