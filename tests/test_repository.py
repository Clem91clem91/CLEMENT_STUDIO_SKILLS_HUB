from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.repository import validate_repository
from clement_skills_hub.schema import load_json, validate_schema


class RepositoryTests(unittest.TestCase):
    def test_bootstrap_repository_is_valid(self) -> None:
        self.assertEqual(validate_repository(ROOT), [])

    def test_invalid_manifest_status_is_rejected_by_schema(self) -> None:
        schema = load_json(ROOT / "schemas" / "skill.schema.json")
        manifest = {
            "schema_version": "1.0.0",
            "id": "clement.example.0123456789ab",
            "name": "example",
            "version": "1.0.0",
            "status": "UNKNOWN",
            "category": "other",
            "description": "",
            "sha256": "A" * 64,
            "content_path": "skills/other/clement.example.0123456789ab/SKILL.md",
            "source": {
                "canonical_path": "lib/example/SKILL.md",
                "library": "lib",
                "replica_count": 1,
                "replicas": ["lib/example/SKILL.md"],
                "manifest_sha256": None,
            },
            "keywords": [],
            "dependencies": [],
            "conflicts": [],
            "unresolved_dependencies": [],
            "unresolved_conflicts": [],
            "estimated_context_cost": 1,
            "validation_notes": [],
        }
        errors = validate_schema(manifest, schema)
        self.assertTrue(any("enum" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

