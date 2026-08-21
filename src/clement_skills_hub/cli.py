"""Machine-readable command line interface used by PowerShell and CI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import verify_audit_inputs, verify_evidence_files
from .errors import SkillsHubError
from .importer import apply_import_plan, build_import_plan
from .models import AuditContract
from .repository import validate_repository


def _path(value: str) -> Path:
    return Path(value).expanduser()


def _add_audit_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source-root", required=True, type=_path)
    parser.add_argument("--inventory", required=True, type=_path)
    parser.add_argument("--contract", required=True, type=_path)
    parser.add_argument("--audit-report", required=True, type=_path)
    parser.add_argument("--evidence-index", required=True, type=_path)
    parser.add_argument("--audit-bundle", required=True, type=_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clement-skills-hub")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a Hub checkout")
    validate_parser.add_argument("--root", required=True, type=_path)

    audit_parser = subparsers.add_parser("audit", help="verify audit evidence and source")
    _add_audit_arguments(audit_parser)

    plan_parser = subparsers.add_parser("plan", help="build an import plan without applying it")
    _add_audit_arguments(plan_parser)

    import_parser = subparsers.add_parser("import", help="plan or transactionally apply import")
    _add_audit_arguments(import_parser)
    import_parser.add_argument("--repository-root", required=True, type=_path)
    import_parser.add_argument("--apply", action="store_true")
    import_parser.add_argument("--backup-root", type=_path)
    return parser


def _load_and_verify_evidence(arguments: argparse.Namespace) -> AuditContract:
    contract = AuditContract.load(arguments.contract)
    verify_evidence_files(
        contract,
        inventory_path=arguments.inventory,
        audit_report=arguments.audit_report,
        evidence_index=arguments.evidence_index,
        audit_bundle=arguments.audit_bundle,
    )
    return contract


def _print_plan(plan: object) -> None:
    metrics = plan.metrics
    print(f"TOTAL_SKILL_FILES={metrics.total_skill_files}")
    print(f"UNIQUE_BY_SHA256={metrics.unique_by_sha256}")
    print(f"EXACT_DUPLICATES={metrics.exact_duplicates}")
    print(f"UNIQUE_SKILL_NAMES={metrics.unique_skill_names}")
    print(f"NAME_CONFLICTS={metrics.name_conflicts}")
    print(f"INCOMPLETE_SKILLS={metrics.incomplete_skills}")
    print(f"INVALID_MANIFESTS={metrics.invalid_manifests}")
    print(f"NORMALIZED_ENTRIES={len(plan.skills)}")
    print(f"SOURCE_SNAPSHOT_SHA256={plan.source_snapshot_sha256}")
    print(f"CONTENT_FINGERPRINT={plan.content_fingerprint}")


def run(arguments: argparse.Namespace) -> int:
    if arguments.command == "validate":
        errors = validate_repository(arguments.root.resolve())
        if errors:
            print("SKILLS_HUB_TESTS=FAIL")
            for error in errors:
                print(f"ERROR={error}")
            return 1
        print("SKILLS_HUB_TESTS=PASS")
        print("RESULT=PASS")
        return 0

    contract = _load_and_verify_evidence(arguments)
    if arguments.command == "audit":
        _, _, metrics = verify_audit_inputs(
            arguments.source_root,
            arguments.inventory,
            contract,
        )
        for key, value in metrics.as_dict().items():
            print(f"{key.upper()}={value}")
        print("SOURCE_WRITE_OPERATIONS=0")
        print("RESULT=PASS")
        return 0

    plan = build_import_plan(arguments.source_root, arguments.inventory, contract)
    _print_plan(plan)
    if arguments.command == "plan" or not arguments.apply:
        print("MODE=DRY_RUN")
        print("FILE_CHANGED=NO")
        print("RESULT=PASS")
        return 0

    if arguments.backup_root is None:
        raise SkillsHubError("--backup-root is mandatory with --apply")
    repository_root = arguments.repository_root.resolve(strict=True)
    result = apply_import_plan(repository_root, plan, contract, arguments.backup_root)
    errors = validate_repository(repository_root)
    if errors:
        raise SkillsHubError("repository validation after apply failed: " + "; ".join(errors[:30]))
    print("MODE=APPLY")
    print(f"APPLY_RESULT={result.result}")
    print(f"FILE_CHANGED={'YES' if result.changed else 'NO'}")
    print(f"BACKUP_PATH={result.backup_path or 'NOT_REQUIRED'}")
    print(f"BEFORE_SHA256={result.before_fingerprint}")
    print(f"AFTER_SHA256={result.after_fingerprint}")
    print(f"REGISTRY_PATH={result.registry_path}")
    print("SKILLS_HUB_TESTS=PASS")
    print("RESULT=PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        return run(arguments)
    except (SkillsHubError, OSError, ValueError) as exc:
        message = str(exc).replace("\r", " ").replace("\n", " ")
        print("RESULT=FAIL")
        print(f"ERROR_TYPE={type(exc).__name__}")
        print(f"ERROR_MESSAGE={message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
