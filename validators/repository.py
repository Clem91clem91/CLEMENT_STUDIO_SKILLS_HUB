from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

VALID_STATUSES = {
    "ACTIVE",
    "CANDIDATE",
    "NEEDS_REVIEW",
    "DEPRECATED",
    "ARCHIVED",
    "CONFLICT",
    "INCOMPLETE",
}

VALID_CATEGORIES = {
    "coding",
    "documents",
    "research",
    "3d",
    "blender",
    "unreal",
    "comfyui",
    "filesystem",
    "github",
    "orchestration",
    "security",
    "other",
}

REQUIRED_PATHS = (
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
    "registry/skills_registry.json",
    "schemas/skill.schema.json",
    "docs/audit/SKILLS_LIBRARY_AUDIT.md",
    "docs/audit/AUDIT_PROVENANCE.json",
    "docs/audit/evidence/skills_inventory.csv",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def is_true(value: object) -> bool:
    return str(value).strip().lower() == "true"


def compute_audit_metrics(rows: list[dict[str, str]]) -> dict[str, int]:
    skill_rows = [row for row in rows if is_true(row.get("HasSkill"))]
    hashes = {
        row["SkillSha256"].strip().upper()
        for row in skill_rows
        if row.get("SkillSha256", "").strip()
    }

    normalized_names = {
        row.get("NormalizedName", "").strip().lower()
        for row in rows
        if row.get("NormalizedName", "").strip()
    }

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        groups[row.get("NormalizedName", "").strip().lower()].append(row)

    name_conflicts = 0

    for group in groups.values():
        distinct_hashes = {
            row.get("SkillSha256", "").strip().upper()
            for row in group
            if row.get("SkillSha256", "").strip()
        }
        has_missing_hash = any(
            not row.get("SkillSha256", "").strip()
            for row in group
        )

        if len(group) > 1 and (len(distinct_hashes) > 1 or has_missing_hash):
            name_conflicts += 1

    incomplete = sum(
        row.get("AuditStatus", "").strip().upper() == "INCOMPLETE"
        for row in rows
    )

    invalid_manifests = sum(
        is_true(row.get("HasManifest"))
        and not is_true(row.get("ManifestValid"))
        for row in rows
    )

    return {
        "total_skill_files": len(skill_rows),
        "unique_by_sha256": len(hashes),
        "exact_duplicates": len(skill_rows) - len(hashes),
        "unique_skill_names": len(normalized_names),
        "name_conflicts": name_conflicts,
        "incomplete_skills": incomplete,
        "invalid_manifests": invalid_manifests,
    }


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")

    for category in VALID_CATEGORIES:
        if not (root / "skills" / category).is_dir():
            errors.append(f"missing category directory: skills/{category}")

    if errors:
        return errors

    registry = load_json(root / "registry" / "skills_registry.json")
    schema = load_json(root / "schemas" / "skill.schema.json")
    provenance = load_json(root / "docs" / "audit" / "AUDIT_PROVENANCE.json")

    report_path = root / "docs" / "audit" / "SKILLS_LIBRARY_AUDIT.md"
    report_hash = sha256_file(report_path)

    if report_hash != provenance.get("report_sha256", "").upper():
        errors.append("audit report SHA256 mismatch")

    inventory_path = root / "docs" / "audit" / "evidence" / "skills_inventory.csv"

    with inventory_path.open("r", encoding="utf-8-sig", newline="") as stream:
        inventory_rows = list(csv.DictReader(stream))

    actual_metrics = compute_audit_metrics(inventory_rows)
    expected_metrics = provenance.get("metrics", {})

    for metric_name, actual_value in actual_metrics.items():
        expected_value = expected_metrics.get(metric_name)

        if expected_value != actual_value:
            errors.append(
                f"audit metric mismatch: {metric_name}: "
                f"expected={expected_value!r}, actual={actual_value!r}"
            )

    schema_statuses = set(
        schema.get("properties", {})
        .get("status", {})
        .get("enum", [])
    )

    if schema_statuses != VALID_STATUSES:
        errors.append("schema status enum mismatch")

    schema_categories = set(
        schema.get("properties", {})
        .get("category", {})
        .get("enum", [])
    )

    if schema_categories != VALID_CATEGORIES:
        errors.append("schema category enum mismatch")

    skills = registry.get("skills")

    if not isinstance(skills, list):
        errors.append("registry.skills must be a list")
        return errors

    seen_ids: set[str] = set()
    seen_names: set[str] = set()

    required_fields = {
        "id",
        "name",
        "version",
        "status",
        "category",
        "description",
        "sha256",
        "source",
    }

    for index, skill in enumerate(skills):
        if not isinstance(skill, dict):
            errors.append(f"registry skill #{index} is not an object")
            continue

        missing_fields = sorted(required_fields - set(skill))

        if missing_fields:
            errors.append(
                f"registry skill #{index} missing fields: "
                + ", ".join(missing_fields)
            )
            continue

        skill_id = str(skill["id"]).strip()
        normalized_name = str(skill["name"]).strip().lower()

        if skill_id in seen_ids:
            errors.append(f"duplicate skill id: {skill_id}")
        seen_ids.add(skill_id)

        if normalized_name in seen_names:
            errors.append(f"duplicate skill name: {normalized_name}")
        seen_names.add(normalized_name)

        if skill["status"] not in VALID_STATUSES:
            errors.append(f"invalid status for {skill_id}: {skill['status']}")

        if skill["category"] not in VALID_CATEGORIES:
            errors.append(f"invalid category for {skill_id}: {skill['category']}")

        if not re.fullmatch(r"[A-Fa-f0-9]{64}", str(skill["sha256"])):
            errors.append(f"invalid SHA256 for {skill_id}")

    return errors