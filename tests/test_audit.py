from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.audit import assert_metrics_contract, compute_metrics
from clement_skills_hub.models import AuditMetrics
from tests.helpers import metric_records


class AuditMetricsTests(unittest.TestCase):
    def test_certified_scale_metrics_are_reproduced(self) -> None:
        records = metric_records(
            unique_count=905,
            duplicate_count=900,
            incomplete_count=5,
        )
        actual = compute_metrics(records)
        expected = AuditMetrics(
            total_skill_files=1805,
            unique_by_sha256=905,
            exact_duplicates=900,
            unique_skill_names=905,
            name_conflicts=0,
            incomplete_skills=5,
            invalid_manifests=0,
        )
        self.assertEqual(actual, expected)
        assert_metrics_contract(actual, expected)

    def test_same_name_with_different_hash_is_a_conflict(self) -> None:
        records = metric_records(unique_count=2, duplicate_count=0, incomplete_count=0)
        changed = records[1]
        records[1] = type(changed)(
            **{
                field: (
                    records[0].normalized_name
                    if field == "normalized_name"
                    else records[0].skill_name
                    if field == "skill_name"
                    else getattr(changed, field)
                )
                for field in changed.__dataclass_fields__
            }
        )
        self.assertEqual(compute_metrics(records).name_conflicts, 1)


if __name__ == "__main__":
    unittest.main()

