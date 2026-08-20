from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clement_skills_hub.audit import verify_evidence_files
from clement_skills_hub.constants import REQUIRED_INVENTORY_COLUMNS
from clement_skills_hub.errors import AuditContractError
from clement_skills_hub.hashing import sha256_file
from clement_skills_hub.models import AuditContract, AuditMetrics


class EvidenceTests(unittest.TestCase):
    def test_inventory_is_bound_by_evidence_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory = root / "skills_inventory.csv"
            report = root / "report.md"
            bundle = root / "bundle.zip"
            index = root / "evidence.txt"
            inventory.write_text("header\nvalue\n", encoding="utf-8")
            report.write_text("report", encoding="utf-8")
            bundle.write_bytes(b"bundle")
            index.write_text(
                f"{sha256_file(inventory)}  C:\\audit\\skills_inventory.csv\n",
                encoding="utf-8",
            )
            contract = AuditContract(
                contract_version="1.0.0",
                source_root=str(root),
                source_snapshot_sha256="A" * 64,
                report_sha256=sha256_file(report),
                evidence_index_sha256=sha256_file(index),
                audit_bundle_sha256=sha256_file(bundle),
                metrics=AuditMetrics(0, 0, 0, 0, 0, 0, 0),
                required_inventory_columns=REQUIRED_INVENTORY_COLUMNS,
            )
            verify_evidence_files(
                contract,
                inventory_path=inventory,
                audit_report=report,
                evidence_index=index,
                audit_bundle=bundle,
            )
            inventory.write_text("tampered", encoding="utf-8")
            with self.assertRaises(AuditContractError):
                verify_evidence_files(
                    contract,
                    inventory_path=inventory,
                    audit_report=report,
                    evidence_index=index,
                    audit_bundle=bundle,
                )


if __name__ == "__main__":
    unittest.main()

