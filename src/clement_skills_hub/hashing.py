"""Canonical SHA256 helpers."""

from __future__ import annotations

import hashlib
import json
import locale
from pathlib import Path
from typing import Iterable, Mapping


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(data: object) -> str:
    """Return stable UTF-8 JSON with a final newline."""

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        separators=(",", ": "),
    ) + "\n"


def inventory_snapshot_sha256(path_hashes: Mapping[str, str]) -> str:
    """Reproduce the certified PowerShell snapshot algorithm.

    The original audit sorted absolute candidate paths, joined each raw path
    and uppercase hash with a tab, then SHA256-hashed UTF-8 text.
    """

    lines = [
        f"{path}\t{path_hashes[path].upper()}"
        for path in sorted(path_hashes)
    ]
    return sha256_text("\n".join(lines))


def inventory_snapshot_candidates(path_hashes: Mapping[str, str]) -> set[str]:
    """Return safe order variants used by PowerShell/.NET string sorting.

    PowerShell's ``Sort-Object`` is culture-aware and case-insensitive whereas
    Python's default ordering is ordinal. The certified inventory file itself
    is separately SHA256-bound by the evidence index; accepting only these
    deterministic order variants avoids a false negative across Windows locale
    configurations without weakening any file-level hash check.
    """

    paths = list(path_hashes)
    orders: list[list[str]] = [
        sorted(paths),
        sorted(paths, key=lambda item: (item.casefold(), item)),
    ]
    try:
        locale.setlocale(locale.LC_COLLATE, "")
        orders.append(sorted(paths, key=lambda item: locale.strxfrm(item.casefold())))
    except locale.Error:
        pass
    results: set[str] = set()
    for order in orders:
        lines = [f"{path}\t{path_hashes[path].upper()}" for path in order]
        results.add(sha256_text("\n".join(lines)))
    return results


def content_fingerprint(items: Iterable[tuple[str, bytes]]) -> str:
    """Fingerprint a tree independently of the host absolute path."""

    lines = [
        f"{relative_path.replace(chr(92), '/')}\t{sha256_bytes(payload)}"
        for relative_path, payload in items
    ]
    return sha256_text("\n".join(sorted(lines)))


def tree_fingerprint(root: Path, *, excluded_names: frozenset[str] = frozenset()) -> str:
    items: list[tuple[str, bytes]] = []
    if not root.exists():
        return sha256_text("")

    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if any(part in excluded_names for part in path.relative_to(root).parts):
            continue
        items.append((path.relative_to(root).as_posix(), path.read_bytes()))
    return content_fingerprint(items)
