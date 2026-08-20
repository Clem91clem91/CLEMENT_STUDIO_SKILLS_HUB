from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.errors import SourceIntegrityError
from clement_skills_hub.paths import resolved_descendant


class SourcePathSecurityTests(unittest.TestCase):
    def test_path_outside_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            outside = base / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            with self.assertRaises(SourceIntegrityError):
                resolved_descendant(source, outside)


if __name__ == "__main__":
    unittest.main()

