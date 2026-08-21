from __future__ import annotations

import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.importer import build_import_plan
from tests.helpers import create_dataset


class CertifiedScaleTests(unittest.TestCase):
    def test_exact_1805_to_905_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            inventory, contract = create_dataset(
                source,
                unique_count=905,
                duplicate_count=900,
                incomplete_count=5,
            )
            plan = build_import_plan(source, inventory, contract)
            self.assertEqual(plan.metrics.total_skill_files, 1805)
            self.assertEqual(plan.metrics.unique_by_sha256, 905)
            self.assertEqual(plan.metrics.exact_duplicates, 900)
            self.assertEqual(len(plan.skills), 905)
            statuses = Counter(skill.manifest["status"] for skill in plan.skills)
            self.assertEqual(statuses["INCOMPLETE"], 5)
            self.assertEqual(statuses["CANDIDATE"], 900)


if __name__ == "__main__":
    unittest.main()

