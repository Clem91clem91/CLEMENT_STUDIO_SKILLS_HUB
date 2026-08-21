from __future__ import annotations

import csv
import json
from pathlib import Path

from clement_skills_hub.constants import REQUIRED_INVENTORY_COLUMNS
from clement_skills_hub.hashing import inventory_snapshot_sha256, sha256_file
from clement_skills_hub.models import AuditContract, AuditMetrics, AuditRecord


FIELD_ORDER = (
    "SkillName",
    "NormalizedName",
    "NameSource",
    "RootPath",
    "HasSkill",
    "SkillPath",
    "SkillSha256",
    "HasManifest",
    "ManifestPath",
    "ManifestSha256",
    "ManifestValid",
    "ManifestNamePresent",
    "ManifestError",
    "AuditStatus",
)


def metric_records(
    *, unique_count: int, duplicate_count: int, incomplete_count: int
) -> list[AuditRecord]:
    records: list[AuditRecord] = []
    for index in range(unique_count):
        digest = f"{index:064X}"
        incomplete = index >= unique_count - incomplete_count
        records.append(
            AuditRecord(
                skill_name=f"skill-{index:04d}",
                normalized_name=f"skill-{index:04d}",
                name_source="SKILL_FRONT_MATTER",
                root_path=f"/source/lib-a/skill-{index:04d}",
                has_skill=True,
                skill_path=f"/source/lib-a/skill-{index:04d}/SKILL.md",
                skill_sha256=digest,
                has_manifest=not incomplete,
                manifest_path=(f"/source/lib-a/skill-{index:04d}/manifest.json" if not incomplete else ""),
                manifest_sha256=(f"{index + 10000:064X}" if not incomplete else ""),
                manifest_valid=not incomplete,
                manifest_name_present=not incomplete,
                manifest_error="",
                audit_status="INCOMPLETE" if incomplete else "COMPLETE_CANDIDATE",
            )
        )
    for index in range(duplicate_count):
        original = records[index]
        records.append(
            AuditRecord(
                skill_name=original.skill_name,
                normalized_name=original.normalized_name,
                name_source=original.name_source,
                root_path=f"/source/lib-b/skill-{index:04d}",
                has_skill=True,
                skill_path=f"/source/lib-b/skill-{index:04d}/SKILL.md",
                skill_sha256=original.skill_sha256,
                has_manifest=True,
                manifest_path=f"/source/lib-b/skill-{index:04d}/manifest.json",
                manifest_sha256=f"{index + 10000:064X}",
                manifest_valid=True,
                manifest_name_present=True,
                manifest_error="",
                audit_status="COMPLETE_CANDIDATE",
            )
        )
    return records


def create_dataset(
    root: Path,
    *,
    unique_count: int,
    duplicate_count: int,
    incomplete_count: int,
) -> tuple[Path, AuditContract]:
    rows: list[dict[str, str]] = []
    path_hashes: dict[str, str] = {}

    def add_copy(library: str, index: int, *, incomplete: bool) -> None:
        name = f"skill-{index:04d}"
        skill_root = root / library / name
        skill_root.mkdir(parents=True, exist_ok=True)
        content = (
            f"---\nname: {name}\ndescription: Synthetic skill {index}\n---\n"
            f"# {name}\n\nDeterministic content {index}.\n"
        ).encode("utf-8")
        skill_path = skill_root / "SKILL.md"
        skill_path.write_bytes(content)
        skill_hash = sha256_file(skill_path)
        manifest_path = skill_root / "manifest.json"
        manifest_hash = ""
        if not incomplete:
            manifest_path.write_text(
                json.dumps(
                    {
                        "name": name,
                        "version": "1.0.0",
                        "description": f"Synthetic skill {index}",
                        "keywords": ["synthetic", "coding"],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            manifest_hash = sha256_file(manifest_path)
        row = {
            "SkillName": name,
            "NormalizedName": name,
            "NameSource": "SKILL_FRONT_MATTER",
            "RootPath": str(skill_root),
            "HasSkill": "True",
            "SkillPath": str(skill_path),
            "SkillSha256": skill_hash,
            "HasManifest": str(not incomplete),
            "ManifestPath": str(manifest_path) if not incomplete else "",
            "ManifestSha256": manifest_hash,
            "ManifestValid": str(not incomplete),
            "ManifestNamePresent": str(not incomplete),
            "ManifestError": "",
            "AuditStatus": "INCOMPLETE" if incomplete else "COMPLETE_CANDIDATE",
        }
        rows.append(row)
        path_hashes[str(skill_path)] = skill_hash
        if not incomplete:
            path_hashes[str(manifest_path)] = manifest_hash

    for index in range(unique_count):
        add_copy(
            "lib-a",
            index,
            incomplete=index >= unique_count - incomplete_count,
        )
    for index in range(duplicate_count):
        add_copy("lib-b", index, incomplete=False)

    inventory = root / "skills_inventory.csv"
    with inventory.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELD_ORDER)
        writer.writeheader()
        writer.writerows(rows)

    metrics = AuditMetrics(
        total_skill_files=unique_count + duplicate_count,
        unique_by_sha256=unique_count,
        exact_duplicates=duplicate_count,
        unique_skill_names=unique_count,
        name_conflicts=0,
        incomplete_skills=incomplete_count,
        invalid_manifests=0,
    )
    contract = AuditContract(
        contract_version="1.0.0",
        source_root=str(root),
        source_snapshot_sha256=inventory_snapshot_sha256(path_hashes),
        report_sha256="A" * 64,
        evidence_index_sha256="B" * 64,
        audit_bundle_sha256="C" * 64,
        metrics=metrics,
        required_inventory_columns=REQUIRED_INVENTORY_COLUMNS,
    )
    return inventory, contract

