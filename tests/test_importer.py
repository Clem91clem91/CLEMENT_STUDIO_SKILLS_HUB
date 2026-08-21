from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.constants import VALID_CATEGORIES
from clement_skills_hub.hashing import tree_fingerprint
from clement_skills_hub.importer import (
    apply_import_plan,
    build_import_plan,
    materialize_plan,
)
from clement_skills_hub.repository import validate_payload
from clement_skills_hub.schema import load_json
from tests.helpers import create_dataset


class ImporterTests(unittest.TestCase):
    def test_plan_is_deterministic_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            inventory, contract = create_dataset(
                source,
                unique_count=3,
                duplicate_count=2,
                incomplete_count=1,
            )
            before = tree_fingerprint(source)
            first = build_import_plan(source, inventory, contract)
            second = build_import_plan(source, inventory, contract)
            after = tree_fingerprint(source)
            self.assertEqual(first.content_fingerprint, second.content_fingerprint)
            self.assertEqual(first.registry, second.registry)
            self.assertEqual(before, after)
            self.assertEqual(len(first.skills), 3)
            statuses = Counter(skill.manifest["status"] for skill in first.skills)
            self.assertEqual(statuses, {"CANDIDATE": 2, "INCOMPLETE": 1})
            duplicate = next(
                skill for skill in first.skills if skill.manifest["source"]["replica_count"] == 2
            )
            self.assertEqual(len(duplicate.manifest["source"]["replicas"]), 2)

    def test_materialized_payload_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            inventory, contract = create_dataset(
                source,
                unique_count=4,
                duplicate_count=2,
                incomplete_count=1,
            )
            plan = build_import_plan(source, inventory, contract)
            destination = base / "payload"
            materialize_plan(plan, destination)
            schema = load_json(ROOT / "schemas" / "skill.schema.json")
            self.assertEqual(
                validate_payload(destination / "skills", plan.registry, schema, contract),
                [],
            )

            populated = {str(skill.manifest["category"]) for skill in plan.skills}
            for category in VALID_CATEGORIES:
                category_root = destination / "skills" / category
                self.assertTrue(category_root.is_dir(), category)
                if category not in populated:
                    self.assertTrue((category_root / ".gitkeep").is_file(), category)

    def test_transaction_is_backed_up_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            inventory, contract = create_dataset(
                source,
                unique_count=3,
                duplicate_count=1,
                incomplete_count=1,
            )
            plan = build_import_plan(source, inventory, contract)
            repository = base / "repository"
            (repository / "schemas").mkdir(parents=True)
            (repository / "registry").mkdir()
            (repository / "skills" / "other").mkdir(parents=True)
            shutil.copy2(ROOT / "schemas" / "skill.schema.json", repository / "schemas")
            (repository / "registry" / "skills_registry.json").write_text(
                '{"state":"BOOTSTRAP"}\n', encoding="utf-8"
            )
            backup_root = base / "backups"
            first = apply_import_plan(repository, plan, contract, backup_root)
            self.assertTrue(first.changed)
            self.assertIsNotNone(first.backup_path)
            self.assertTrue((first.backup_path / "BACKUP_RECEIPT.json").is_file())
            second = apply_import_plan(repository, plan, contract, backup_root)
            self.assertFalse(second.changed)
            self.assertEqual(second.result, "NO_CHANGE")
            self.assertEqual(first.after_fingerprint, second.after_fingerprint)
            registry = json.loads(
                (repository / "registry" / "skills_registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry["stats"]["total_entries"], 3)


if __name__ == "__main__":
    unittest.main()
