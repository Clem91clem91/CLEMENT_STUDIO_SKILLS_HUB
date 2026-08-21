"""Load and independently recompute certified audit evidence."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .errors import AuditContractError, SourceIntegrityError
from .hashing import inventory_snapshot_candidates, sha256_file
from .models import AuditContract, AuditMetrics, AuditRecord, SourceReplica
from .paths import relative_source_path, same_location, source_path


def load_inventory(path: Path) -> list[AuditRecord]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise AuditContractError("audit inventory has no CSV header")
            records = [AuditRecord.from_row(row) for row in reader]
    except OSError as exc:
        raise AuditContractError(f"cannot read audit inventory {path}: {exc}") from exc
    if not records:
        raise AuditContractError("audit inventory is empty")
    return records


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789ABCDEF" for character in value)


def compute_metrics(records: Iterable[AuditRecord]) -> AuditMetrics:
    rows = list(records)
    skill_rows = [record for record in rows if record.has_skill]
    hashes = {record.skill_sha256 for record in skill_rows if record.skill_sha256}
    names = {record.normalized_name for record in rows if record.normalized_name}

    groups: dict[str, list[AuditRecord]] = defaultdict(list)
    for record in rows:
        groups[record.normalized_name].append(record)

    conflicts = 0
    for name, group in groups.items():
        if not name or len(group) < 2:
            continue
        distinct_hashes = {record.skill_sha256 for record in group if record.skill_sha256}
        missing_hash = any(not record.skill_sha256 for record in group)
        if len(distinct_hashes) > 1 or missing_hash:
            conflicts += 1

    return AuditMetrics(
        total_skill_files=len(skill_rows),
        unique_by_sha256=len(hashes),
        exact_duplicates=len(skill_rows) - len(hashes),
        unique_skill_names=len(names),
        name_conflicts=conflicts,
        incomplete_skills=sum(record.audit_status == "INCOMPLETE" for record in rows),
        invalid_manifests=sum(
            record.has_manifest and not record.manifest_valid for record in rows
        ),
    )


def assert_metrics_contract(actual: AuditMetrics, expected: AuditMetrics) -> None:
    differences = []
    for field in actual.__dataclass_fields__:
        actual_value = getattr(actual, field)
        expected_value = getattr(expected, field)
        if actual_value != expected_value:
            differences.append(f"{field}: expected={expected_value}, actual={actual_value}")
    if differences:
        raise AuditContractError("audit metric mismatch: " + "; ".join(differences))


def inventory_path_hashes(records: Iterable[AuditRecord]) -> dict[str, str]:
    result: dict[str, str] = {}
    for record in records:
        pairs: tuple[tuple[bool, str, str, str], ...] = (
            (record.has_skill, record.skill_path, record.skill_sha256, "SKILL.md"),
            (record.has_manifest, record.manifest_path, record.manifest_sha256, "manifest.json"),
        )
        for present, raw_path, digest, label in pairs:
            if not present:
                continue
            if not raw_path or not _valid_sha256(digest):
                raise AuditContractError(
                    f"invalid {label} path/hash for inventory root {record.root_path}"
                )
            previous = result.get(raw_path)
            if previous is not None and previous != digest:
                raise AuditContractError(f"same source path has two hashes: {raw_path}")
            result[raw_path] = digest
    return result


def assert_inventory_snapshot(records: Iterable[AuditRecord], expected_sha256: str) -> str:
    candidates = inventory_snapshot_candidates(inventory_path_hashes(records))
    if expected_sha256 not in candidates:
        raise AuditContractError(
            "audit inventory snapshot mismatch: "
            f"expected={expected_sha256}, candidates={sorted(candidates)}"
        )
    return expected_sha256


def verify_evidence_files(
    contract: AuditContract,
    *,
    inventory_path: Path,
    audit_report: Path,
    evidence_index: Path,
    audit_bundle: Path,
) -> None:
    evidence = (
        ("audit report", audit_report, contract.report_sha256),
        ("evidence index", evidence_index, contract.evidence_index_sha256),
        ("audit bundle", audit_bundle, contract.audit_bundle_sha256),
    )
    for label, path, expected in evidence:
        if not path.is_file():
            raise AuditContractError(f"{label} not found: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise AuditContractError(
                f"{label} SHA256 mismatch: expected={expected}, actual={actual}, path={path}"
            )

    try:
        index_lines = evidence_index.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditContractError(f"cannot read evidence index {evidence_index}: {exc}") from exc
    inventory_hashes: set[str] = set()
    for line in index_lines:
        match = re.match(r"^\s*([A-Fa-f0-9]{64})\s{2,}(.+?)\s*$", line)
        if not match:
            continue
        basename = re.split(r"[\\/]", match.group(2))[-1]
        if basename.casefold() == "skills_inventory.csv":
            inventory_hashes.add(match.group(1).upper())
    if len(inventory_hashes) != 1:
        raise AuditContractError(
            "evidence index must bind exactly one skills_inventory.csv SHA256"
        )
    if not inventory_path.is_file():
        raise AuditContractError(f"audit inventory not found: {inventory_path}")
    actual_inventory_hash = sha256_file(inventory_path)
    expected_inventory_hash = next(iter(inventory_hashes))
    if actual_inventory_hash != expected_inventory_hash:
        raise AuditContractError(
            "audit inventory SHA256 mismatch against evidence index: "
            f"expected={expected_inventory_hash}, actual={actual_inventory_hash}"
        )


def verify_source(
    source_root: Path,
    records: Iterable[AuditRecord],
    *,
    expected_contract_root: str | None = None,
) -> list[SourceReplica]:
    if expected_contract_root is not None and not same_location(source_root, expected_contract_root):
        raise SourceIntegrityError(
            "runtime source root differs from certified contract: "
            f"expected={expected_contract_root}, actual={source_root}"
        )
    if not source_root.is_dir():
        raise SourceIntegrityError(f"certified source root not found: {source_root}")

    replicas: list[SourceReplica] = []
    for record in records:
        if not record.has_skill:
            continue
        skill = source_path(source_root, record.skill_path)
        actual_skill_hash = sha256_file(skill)
        if actual_skill_hash != record.skill_sha256:
            raise SourceIntegrityError(
                f"SKILL.md changed: {skill}: expected={record.skill_sha256}, "
                f"actual={actual_skill_hash}"
            )

        manifest: Path | None = None
        relative_manifest: str | None = None
        if record.has_manifest:
            manifest = source_path(source_root, record.manifest_path)
            actual_manifest_hash = sha256_file(manifest)
            if actual_manifest_hash != record.manifest_sha256:
                raise SourceIntegrityError(
                    f"manifest.json changed: {manifest}: "
                    f"expected={record.manifest_sha256}, actual={actual_manifest_hash}"
                )
            relative_manifest = relative_source_path(source_root, manifest)

        replicas.append(
            SourceReplica(
                record=record,
                skill_path=skill,
                manifest_path=manifest,
                relative_skill_path=relative_source_path(source_root, skill),
                relative_manifest_path=relative_manifest,
            )
        )
    return replicas


def verify_audit_inputs(
    source_root: Path,
    inventory_path: Path,
    contract: AuditContract,
    *,
    enforce_contract_root: bool = True,
) -> tuple[list[AuditRecord], list[SourceReplica], AuditMetrics]:
    records = load_inventory(inventory_path)
    metrics = compute_metrics(records)
    assert_metrics_contract(metrics, contract.metrics)
    assert_inventory_snapshot(records, contract.source_snapshot_sha256)
    replicas = verify_source(
        source_root,
        records,
        expected_contract_root=contract.source_root if enforce_contract_root else None,
    )
    if len({replica.record.skill_sha256 for replica in replicas}) != metrics.unique_by_sha256:
        raise AuditContractError("verified source unique hash count differs from audit metrics")
    return records, replicas, metrics
