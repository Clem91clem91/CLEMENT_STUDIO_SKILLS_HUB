from __future__ import annotations

import hashlib
import json
from pathlib import Path

from clement_skills_hub.extensions import effective_skill_entries, load_native_registry


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_NATIVE_NAMES = {
    "cyber-domain-intelligence",
    "cyber-ip-intelligence",
    "cyber-web-security-audit",
    "cyber-threat-intelligence",
    "cyber-file-triage",
    "cyber-osint-investigation",
    "cyber-network-diagnostics",
    "cyber-incident-triage",
}

CATEGORY_OVERRIDE_IDS = {
    "clement.cybersecurity-analyst.4aa20fe9b6f6",
    "clement.incident-responder.7193756d47a2",
    "clement.network-engineer.59153530c811",
    "clement.penetration-tester.f5e4c13fbd5a",
}


def test_native_cyber_skills_are_complete_and_hashed() -> None:
    registry = load_native_registry(ROOT)
    entries = registry["skills"]
    assert len(entries) == 8
    assert {entry["name"] for entry in entries} == EXPECTED_NATIVE_NAMES
    assert {entry["category"] for entry in entries} == {"security"}

    for entry in entries:
        path = ROOT / entry["content_path"]
        assert path.is_file()
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        assert digest == entry["sha256"]
        manifest = json.loads((path.parent / "manifest.json").read_text(encoding="utf-8"))
        assert manifest == entry


def test_effective_registry_preserves_base_and_applies_security_overrides() -> None:
    base = json.loads((ROOT / "registry" / "skills_registry.json").read_text(encoding="utf-8"))
    effective = effective_skill_entries(ROOT)

    assert len(effective) == len(base["skills"]) + 8
    by_id = {entry["id"]: entry for entry in effective}
    for identifier in CATEGORY_OVERRIDE_IDS:
        assert by_id[identifier]["category"] == "security"

    ids = [entry["id"] for entry in effective]
    names = [entry["name"].strip().lower() for entry in effective]
    hashes = [entry["sha256"] for entry in effective]
    assert len(ids) == len(set(ids))
    assert len(names) == len(set(names))
    assert len(hashes) == len(set(hashes))
