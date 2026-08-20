from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validators.repository import (
    VALID_CATEGORIES,
    VALID_STATUSES,
    validate_repository,
)


class RepositoryTests(unittest.TestCase):
    def test_repository_validation(self) -> None:
        self.assertEqual(validate_repository(ROOT), [])

    def test_schema_statuses(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "skill.schema.json").read_text(
                encoding="utf-8-sig"
            )
        )
        statuses = set(schema["properties"]["status"]["enum"])
        self.assertEqual(statuses, VALID_STATUSES)

    def test_schema_categories(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "skill.schema.json").read_text(
                encoding="utf-8-sig"
            )
        )
        categories = set(schema["properties"]["category"]["enum"])
        self.assertEqual(categories, VALID_CATEGORIES)

    def test_registry_bootstrap_is_empty(self) -> None:
        registry = json.loads(
            (ROOT / "registry" / "skills_registry.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(registry["skills"], [])


if __name__ == "__main__":
    unittest.main()