"""Strict data models without a runtime framework dependency."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .constants import REQUIRED_INVENTORY_COLUMNS
from .errors import AuditContractError


def parse_bool(value: object) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no", "", "none"}:
        return False
    raise AuditContractError(f"invalid boolean value in audit inventory: {value!r}")


@dataclass(frozen=True, slots=True)
class AuditMetrics:
    total_skill_files: int
    unique_by_sha256: int
    exact_duplicates: int
    unique_skill_names: int
    name_conflicts: int
    incomplete_skills: int
    invalid_manifests: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "AuditMetrics":
        try:
            return cls(**{field: int(value[field]) for field in cls.__dataclass_fields__})
        except (KeyError, TypeError, ValueError) as exc:
            raise AuditContractError(f"invalid audit metrics: {exc}") from exc

    def as_dict(self) -> dict[str, int]:
        return {
            field: int(getattr(self, field))
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True, slots=True)
class AuditContract:
    contract_version: str
    source_root: str
    source_snapshot_sha256: str
    report_sha256: str
    evidence_index_sha256: str
    audit_bundle_sha256: str
    metrics: AuditMetrics
    required_inventory_columns: frozenset[str]

    @classmethod
    def load(cls, path: Path) -> "AuditContract":
        try:
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AuditContractError(f"cannot read audit contract {path}: {exc}") from exc

        if not isinstance(raw, dict):
            raise AuditContractError("audit contract must be a JSON object")

        try:
            required = frozenset(str(item) for item in raw["required_inventory_columns"])
            contract = cls(
                contract_version=str(raw["contract_version"]),
                source_root=str(raw["source_root"]),
                source_snapshot_sha256=str(raw["source_snapshot_sha256"]).upper(),
                report_sha256=str(raw["report_sha256"]).upper(),
                evidence_index_sha256=str(raw["evidence_index_sha256"]).upper(),
                audit_bundle_sha256=str(raw["audit_bundle_sha256"]).upper(),
                metrics=AuditMetrics.from_mapping(raw["metrics"]),
                required_inventory_columns=required,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise AuditContractError(f"invalid audit contract: {exc}") from exc

        if contract.required_inventory_columns != REQUIRED_INVENTORY_COLUMNS:
            raise AuditContractError(
                "audit contract inventory columns differ from the importer contract"
            )
        for label, digest in (
            ("source_snapshot_sha256", contract.source_snapshot_sha256),
            ("report_sha256", contract.report_sha256),
            ("evidence_index_sha256", contract.evidence_index_sha256),
            ("audit_bundle_sha256", contract.audit_bundle_sha256),
        ):
            if len(digest) != 64 or any(character not in "0123456789ABCDEF" for character in digest):
                raise AuditContractError(f"{label} is not an uppercase SHA256")
        return contract


@dataclass(frozen=True, slots=True)
class AuditRecord:
    skill_name: str
    normalized_name: str
    name_source: str
    root_path: str
    has_skill: bool
    skill_path: str
    skill_sha256: str
    has_manifest: bool
    manifest_path: str
    manifest_sha256: str
    manifest_valid: bool
    manifest_name_present: bool
    manifest_error: str
    audit_status: str

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "AuditRecord":
        missing = sorted(REQUIRED_INVENTORY_COLUMNS - set(row))
        if missing:
            raise AuditContractError(
                "audit inventory row misses columns: " + ", ".join(missing)
            )
        return cls(
            skill_name=str(row["SkillName"]).strip(),
            normalized_name=str(row["NormalizedName"]).strip().lower(),
            name_source=str(row["NameSource"]).strip(),
            root_path=str(row["RootPath"]).strip(),
            has_skill=parse_bool(row["HasSkill"]),
            skill_path=str(row["SkillPath"]).strip(),
            skill_sha256=str(row["SkillSha256"]).strip().upper(),
            has_manifest=parse_bool(row["HasManifest"]),
            manifest_path=str(row["ManifestPath"]).strip(),
            manifest_sha256=str(row["ManifestSha256"]).strip().upper(),
            manifest_valid=parse_bool(row["ManifestValid"]),
            manifest_name_present=parse_bool(row["ManifestNamePresent"]),
            manifest_error=str(row["ManifestError"]).strip(),
            audit_status=str(row["AuditStatus"]).strip().upper(),
        )


@dataclass(frozen=True, slots=True)
class SourceReplica:
    record: AuditRecord
    skill_path: Path
    manifest_path: Path | None
    relative_skill_path: str
    relative_manifest_path: str | None


@dataclass(slots=True)
class PlannedSkill:
    manifest: dict[str, Any]
    content: bytes

    @property
    def identifier(self) -> str:
        return str(self.manifest["id"])


@dataclass(slots=True)
class ImportPlan:
    metrics: AuditMetrics
    source_snapshot_sha256: str
    skills: list[PlannedSkill]
    registry: dict[str, Any]
    content_fingerprint: str


@dataclass(frozen=True, slots=True)
class ApplyResult:
    changed: bool
    result: str
    backup_path: Path | None
    before_fingerprint: str
    after_fingerprint: str
    registry_path: Path

