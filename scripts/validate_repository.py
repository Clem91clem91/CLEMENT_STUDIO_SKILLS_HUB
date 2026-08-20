from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validators.repository import validate_repository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    arguments = parser.parse_args()

    errors = validate_repository(arguments.root.resolve())

    if errors:
        print("SKILLS_HUB_VALIDATION=FAIL")
        for error in errors:
            print(f"ERROR={error}")
        return 1

    print("SKILLS_HUB_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())