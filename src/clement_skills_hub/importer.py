"""Fail-closed planning and transactional application of normalized skills."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit import verify_audit_inputs, verify_source
from .constants import GENERATOR_VERSION, REGISTRY_VERSION, VALID_CATEGORIES
from .errors import ImportPlanError, RepositoryValidationError, TransactionError
from .hashing import canonical_json, sha256_file, tree_fingerprint
from .models import ApplyResult, AuditContract, ImportPlan
from .normalization import normalize_replicas
from .repository import planned_content_fingerprint, skills_tree_fingerprint, validate_payload
from .schema import load_json


def build_import_plan(
    source_root: Path,
    inventory_path: Path,
    contract: AuditContract,
    *,
    enforce_contract_root: bool = True,
) -> ImportPlan:
    records, replicas, metrics = verify_audit_inputs(
        source_root,
        inventory_path,
        contract,
        enforce_contract_root=enforce_contract_root,
    )
    skills = normalize_replicas(replicas)
    if len(skills) != metrics.unique_by_sha256:
        raise ImportPlanError(
            "normalized skill count mismatch: "
            f"expected={metrics.unique_by_sha256}, actual={len(skills)}"
        )

    fingerprint = planned_content_fingerprint(skills)
    statuses = Counter(str(skill.manifest["status"]) for skill in skills)
    categories = Counter(str(skill.manifest["category"]) for skill in skills)
    registry: dict[str, Any] = {
        "registry_version": REGISTRY_VERSION,
        "generator_version": GENERATOR_VERSION,
        "state": "IMPORTED",
        "generated_at": None,
        "source_snapshot_sha256": contract.source_snapshot_sha256,
        "content_fingerprint": fingerprint,
        "audit": metrics.as_dict(),
        "stats": {
            "total_entries": len(skills),
            "by_status": dict(sorted(statuses.items())),
            "by_category": dict(sorted(categories.items())),
        },
        "skills": [skill.manifest for skill in skills],
    }

    # A second complete read closes the time-of-check/time-of-use window. No
    # source file is opened in write mode anywhere in the importer.
    verify_source(
        source_root,
        records,
        expected_contract_root=contract.source_root if enforce_contract_root else None,
    )
    return ImportPlan(
        metrics=metrics,
        source_snapshot_sha256=contract.source_snapshot_sha256,
        skills=skills,
        registry=registry,
        content_fingerprint=fingerprint,
    )


def materialize_plan(plan: ImportPlan, destination_root: Path) -> None:
    if destination_root.exists() and any(destination_root.iterdir()):
        raise ImportPlanError(f"staging directory must be empty: {destination_root}")
    destination_root.mkdir(parents=True, exist_ok=True)
    skills_root = destination_root / "skills"
    populated_categories = {
        str(skill.manifest["category"])
        for skill in plan.skills
        if str(skill.manifest.get("category", "")) in VALID_CATEGORIES
    }
    for category in VALID_CATEGORIES:
        category_root = skills_root / category
        category_root.mkdir(parents=True, exist_ok=True)
        # Git does not track empty directories. Keep a deterministic placeholder
        # for categories with no materialized skill so a fresh clone preserves
        # the repository structure required by validate_repository().
        if category not in populated_categories:
            (category_root / ".gitkeep").write_text("", encoding="utf-8", newline="\n")
    for skill in plan.skills:
        content_path = destination_root / Path(str(skill.manifest["content_path"]))
        content_path.parent.mkdir(parents=True, exist_ok=True)
        content_path.write_bytes(skill.content)
        manifest_path = content_path.parent / "manifest.json"
        manifest_path.write_text(canonical_json(skill.manifest), encoding="utf-8", newline="\n")
    registry_directory = destination_root / "registry"
    registry_directory.mkdir(parents=True, exist_ok=True)
    (registry_directory / "skills_registry.json").write_text(
        canonical_json(plan.registry), encoding="utf-8", newline="\n"
    )


def _copy_current_to_backup(repository_root: Path, backup_path: Path) -> None:
    backup_path.mkdir(parents=True, exist_ok=False)
    current_skills = repository_root / "skills"
    if current_skills.exists():
        shutil.copytree(current_skills, backup_path / "skills")
    current_registry = repository_root / "registry" / "skills_registry.json"
    if current_registry.is_file():
        shutil.copy2(current_registry, backup_path / "skills_registry.json")
    receipt = {
        "repository_root": str(repository_root.resolve()),
        "skills_tree_sha256": tree_fingerprint(current_skills),
        "registry_sha256": sha256_file(current_registry) if current_registry.is_file() else None,
    }
    (backup_path / "BACKUP_RECEIPT.json").write_text(
        canonical_json(receipt), encoding="utf-8", newline="\n"
    )
    if (backup_path / "skills").exists():
        copied_fingerprint = tree_fingerprint(backup_path / "skills")
        if copied_fingerprint != receipt["skills_tree_sha256"]:
            raise TransactionError("backup skills fingerprint mismatch")
    if (backup_path / "skills_registry.json").is_file():
        copied_registry_hash = sha256_file(backup_path / "skills_registry.json")
        if copied_registry_hash != receipt["registry_sha256"]:
            raise TransactionError("backup registry fingerprint mismatch")


def apply_import_plan(
    repository_root: Path,
    plan: ImportPlan,
    contract: AuditContract,
    backup_root: Path,
) -> ApplyResult:
    repository_root = repository_root.resolve(strict=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    skill_schema = load_json(repository_root / "schemas" / "skill.schema.json")
    before_fingerprint = skills_tree_fingerprint(repository_root / "skills")
    target_registry = repository_root / "registry" / "skills_registry.json"
    if before_fingerprint == plan.content_fingerprint and target_registry.is_file():
        try:
            current_registry = json.loads(target_registry.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            current_registry = None
        if current_registry == plan.registry:
            return ApplyResult(
                changed=False,
                result="NO_CHANGE",
                backup_path=None,
                before_fingerprint=before_fingerprint,
                after_fingerprint=before_fingerprint,
                registry_path=target_registry,
            )

    staging = Path(
        tempfile.mkdtemp(prefix=".clement-staging-", dir=str(repository_root.parent))
    )
    old_skills = repository_root.parent / f".clement-old-skills-{uuid.uuid4().hex}"
    backup_path: Path | None = None
    target_skills = repository_root / "skills"
    old_registry_bytes = target_registry.read_bytes() if target_registry.is_file() else None
    skills_swapped = False
    try:
        materialize_plan(plan, staging)
        payload_errors = validate_payload(staging / "skills", plan.registry, skill_schema, contract)
        if payload_errors:
            raise RepositoryValidationError("; ".join(payload_errors[:30]))
        staging_fingerprint = skills_tree_fingerprint(staging / "skills")
        if staging_fingerprint != plan.content_fingerprint:
            raise RepositoryValidationError("staging fingerprint differs from import plan")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = backup_root / f"p0-01_{timestamp}_{before_fingerprint[:12]}"
        _copy_current_to_backup(repository_root, backup_path)

        if target_skills.exists():
            target_skills.rename(old_skills)
        (staging / "skills").rename(target_skills)
        skills_swapped = True
        target_registry.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging / "registry" / "skills_registry.json", target_registry)

        after_fingerprint = skills_tree_fingerprint(target_skills)
        if after_fingerprint != plan.content_fingerprint:
            raise TransactionError("post-apply skills fingerprint mismatch")
        applied_registry = json.loads(target_registry.read_text(encoding="utf-8-sig"))
        errors = validate_payload(target_skills, applied_registry, skill_schema, contract)
        if errors:
            raise RepositoryValidationError("post-apply validation failed: " + "; ".join(errors[:30]))

        if old_skills.exists():
            shutil.rmtree(old_skills)
        return ApplyResult(
            changed=True,
            result="APPLIED",
            backup_path=backup_path,
            before_fingerprint=before_fingerprint,
            after_fingerprint=after_fingerprint,
            registry_path=target_registry,
        )
    except Exception as exc:
        rollback_error: Exception | None = None
        try:
            if skills_swapped and target_skills.exists():
                shutil.rmtree(target_skills)
            if old_skills.exists():
                old_skills.rename(target_skills)
            if old_registry_bytes is None:
                if target_registry.exists():
                    target_registry.unlink()
            else:
                target_registry.parent.mkdir(parents=True, exist_ok=True)
                target_registry.write_bytes(old_registry_bytes)
        except Exception as rollback_exc:  # pragma: no cover - exceptional OS failure
            rollback_error = rollback_exc
        if rollback_error is not None:
            raise TransactionError(
                f"import failed ({exc}); automatic rollback also failed ({rollback_error}); "
                f"backup={backup_path}"
            ) from exc
        if isinstance(exc, (ImportPlanError, RepositoryValidationError, TransactionError)):
            raise
        raise TransactionError(f"import failed and was rolled back: {exc}") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
