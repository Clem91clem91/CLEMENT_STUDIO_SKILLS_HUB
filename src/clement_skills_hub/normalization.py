"""Deterministic normalization of audited source skills."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable

from .constants import (
    CATEGORY_KEYWORDS,
    MANIFEST_SCHEMA_VERSION,
    VALID_CATEGORIES,
)
from .errors import ImportPlanError
from .models import PlannedSkill, SourceReplica


@dataclass(slots=True)
class _PreliminarySkill:
    planned: PlannedSkill
    raw_dependencies: list[str]
    raw_conflicts: list[str]


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def slugify(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = decomposed.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:72].strip("-") or "skill"


def _front_matter(markdown: str) -> dict[str, str]:
    match = re.match(r"^\ufeff?\s*---\s*\r?\n(?P<body>.*?)\r?\n---\s*(?:\r?\n|$)", markdown, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key_value = re.match(r"^\s*([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if not key_value:
            continue
        value = key_value.group(2).strip()
        if value.startswith(("'", '"')) and value.endswith(value[:1]) and len(value) >= 2:
            value = value[1:-1]
        else:
            value = re.split(r"\s+#\s*", value, maxsplit=1)[0].strip()
        result[key_value.group(1).casefold()] = value
    return result


def _first_description(markdown: str) -> str:
    without_front_matter = re.sub(
        r"^\ufeff?\s*---\s*\r?\n.*?\r?\n---\s*(?:\r?\n|$)",
        "",
        markdown,
        count=1,
        flags=re.DOTALL,
    )
    for line in without_front_matter.splitlines():
        text = line.strip()
        if text and not text.startswith(("#", "```", "<!--")):
            return text[:500]
    return ""


def _list_value(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        candidates = re.split(r"[,;\n]", value)
    elif isinstance(value, list):
        candidates = [str(item) for item in value]
    else:
        return []
    return sorted({item.strip() for item in candidates if item.strip()}, key=str.casefold)


def _source_manifest(replica: SourceReplica) -> dict[str, Any]:
    if replica.manifest_path is None or not replica.record.manifest_valid:
        return {}
    try:
        value = json.loads(replica.manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ImportPlanError(f"certified manifest cannot be read: {replica.manifest_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ImportPlanError(f"certified manifest must be an object: {replica.manifest_path}")
    return value


def _semantic_version(value: object) -> str:
    candidate = str(value or "").strip()
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", candidate):
        return candidate
    return "0.1.0"


def _tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return set(re.findall(r"[a-z0-9][a-z0-9-]{1,31}", normalized))


def infer_category(name: str, description: str, source_path_value: str, source_manifest: dict[str, Any]) -> str:
    explicit = str(source_manifest.get("category", "")).strip().lower()
    if explicit in VALID_CATEGORIES:
        return explicit
    haystack = _tokens(" ".join((name, description, source_path_value)))
    scores = {
        category: len(haystack & keywords)
        for category, keywords in CATEGORY_KEYWORDS
    }
    best_score = max(scores.values(), default=0)
    if best_score == 0:
        return "other"
    for category, _ in CATEGORY_KEYWORDS:
        if scores[category] == best_score:
            return category
    return "other"


def _canonical_replica(replicas: list[SourceReplica]) -> SourceReplica:
    return sorted(
        replicas,
        key=lambda replica: (
            not (replica.record.has_manifest and replica.record.manifest_valid),
            replica.record.audit_status == "INCOMPLETE",
            replica.relative_skill_path.casefold(),
            replica.relative_skill_path,
        ),
    )[0]


def _library(relative_skill_path: str) -> str:
    parts = PurePosixPath(relative_skill_path).parts
    return parts[0] if parts else "unknown"


def _preliminary_skill(skill_hash: str, replicas: list[SourceReplica]) -> _PreliminarySkill:
    canonical = _canonical_replica(replicas)
    content = canonical.skill_path.read_bytes()
    try:
        markdown = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ImportPlanError(f"SKILL.md must be UTF-8: {canonical.skill_path}") from exc

    source_manifest = _source_manifest(canonical)
    front_matter = _front_matter(markdown)
    names = {
        normalize_name(replica.record.skill_name)
        for replica in replicas
        if replica.record.skill_name.strip()
    }
    names.discard("")
    if len(names) > 1:
        raise ImportPlanError(
            f"one SHA256 maps to several skill names: {skill_hash}: {sorted(names)}"
        )

    display_name = (
        canonical.record.skill_name.strip()
        or str(source_manifest.get("name", "")).strip()
        or front_matter.get("name", "").strip()
        or canonical.skill_path.parent.name
    )
    if not display_name:
        raise ImportPlanError(f"skill name cannot be determined: {canonical.skill_path}")

    description = (
        str(source_manifest.get("description", "")).strip()
        or front_matter.get("description", "").strip()
        or _first_description(markdown)
    )
    category = infer_category(
        display_name,
        description,
        canonical.relative_skill_path,
        source_manifest,
    )
    slug = slugify(display_name)
    identifier = f"clement.{slug}.{skill_hash[:12].lower()}"
    content_path = f"skills/{category}/{identifier}/SKILL.md"

    raw_keywords = _list_value(source_manifest.get("keywords"))
    keyword_tokens = _tokens(" ".join((display_name, description)))
    keyword_tokens.update(item.casefold() for item in raw_keywords)
    keyword_tokens.add(category)
    keywords = sorted(keyword_tokens)[:48]

    complete_replicas = [
        replica
        for replica in replicas
        if replica.record.has_manifest and replica.record.manifest_valid
    ]
    status = "CANDIDATE" if complete_replicas else "INCOMPLETE"
    source_paths = sorted({replica.relative_skill_path for replica in replicas}, key=str.casefold)

    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "id": identifier,
        "name": display_name,
        "version": _semantic_version(source_manifest.get("version")),
        "status": status,
        "category": category,
        "description": description,
        "sha256": skill_hash,
        "content_path": content_path,
        "source": {
            "canonical_path": canonical.relative_skill_path,
            "library": _library(canonical.relative_skill_path),
            "replica_count": len(source_paths),
            "replicas": source_paths,
            "manifest_sha256": canonical.record.manifest_sha256 or None,
        },
        "keywords": keywords,
        "dependencies": [],
        "conflicts": [],
        "unresolved_dependencies": [],
        "unresolved_conflicts": [],
        "estimated_context_cost": math.ceil(len(content) / 4),
        "validation_notes": [],
    }
    raw_dependencies = _list_value(
        source_manifest.get("dependencies", source_manifest.get("requires"))
    )
    raw_conflicts = _list_value(source_manifest.get("conflicts"))
    return _PreliminarySkill(
        planned=PlannedSkill(manifest=manifest, content=content),
        raw_dependencies=raw_dependencies,
        raw_conflicts=raw_conflicts,
    )


def _reference_indexes(skills: list[_PreliminarySkill]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = defaultdict(set)
    for skill in skills:
        manifest = skill.planned.manifest
        identifier = str(manifest["id"])
        for key in {
            identifier.casefold(),
            normalize_name(str(manifest["name"])),
            slugify(str(manifest["name"])),
        }:
            index[key].add(identifier)
    return index


def _resolve_references(skills: list[_PreliminarySkill]) -> None:
    index = _reference_indexes(skills)
    by_id = {skill.planned.identifier: skill for skill in skills}

    def resolve(value: str) -> str | None:
        candidates: set[str] = set()
        for key in {value.casefold(), normalize_name(value), slugify(value)}:
            candidates.update(index.get(key, set()))
        return next(iter(candidates)) if len(candidates) == 1 else None

    for skill in skills:
        manifest = skill.planned.manifest
        identifier = skill.planned.identifier
        resolved_dependencies: set[str] = set()
        unresolved_dependencies: set[str] = set()
        resolved_conflicts: set[str] = set()
        unresolved_conflicts: set[str] = set()

        for raw_dependency in skill.raw_dependencies:
            resolved = resolve(raw_dependency)
            if resolved is None or resolved == identifier:
                unresolved_dependencies.add(raw_dependency)
            else:
                resolved_dependencies.add(resolved)
        for raw_conflict in skill.raw_conflicts:
            resolved = resolve(raw_conflict)
            if resolved is None or resolved == identifier:
                unresolved_conflicts.add(raw_conflict)
            else:
                resolved_conflicts.add(resolved)

        manifest["dependencies"] = sorted(resolved_dependencies)
        manifest["conflicts"] = sorted(resolved_conflicts)
        manifest["unresolved_dependencies"] = sorted(unresolved_dependencies, key=str.casefold)
        manifest["unresolved_conflicts"] = sorted(unresolved_conflicts, key=str.casefold)

        notes: set[str] = set()
        if unresolved_dependencies:
            notes.add("unresolved_dependencies")
        if unresolved_conflicts:
            notes.add("unresolved_conflicts")
        if resolved_dependencies & resolved_conflicts:
            notes.add("dependency_conflict_overlap")
            manifest["status"] = "CONFLICT"
        elif notes and manifest["status"] == "CANDIDATE":
            manifest["status"] = "NEEDS_REVIEW"
        manifest["validation_notes"] = sorted(notes)

    # Tarjan strongly connected components; cycles are represented explicitly,
    # never silently activated.
    index_counter = 0
    node_indexes: dict[str, int] = {}
    low_links: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index_counter
        node_indexes[node] = index_counter
        low_links[node] = index_counter
        index_counter += 1
        stack.append(node)
        on_stack.add(node)
        for target in by_id[node].planned.manifest["dependencies"]:
            if target not in node_indexes:
                visit(target)
                low_links[node] = min(low_links[node], low_links[target])
            elif target in on_stack:
                low_links[node] = min(low_links[node], node_indexes[target])
        if low_links[node] == node_indexes[node]:
            component: list[str] = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            components.append(component)

    for identifier in sorted(by_id):
        if identifier not in node_indexes:
            visit(identifier)
    for component in components:
        if len(component) <= 1:
            continue
        for identifier in component:
            manifest = by_id[identifier].planned.manifest
            manifest["status"] = "CONFLICT"
            manifest["validation_notes"] = sorted(
                set(manifest["validation_notes"]) | {"dependency_cycle"}
            )


def normalize_replicas(replicas: Iterable[SourceReplica]) -> list[PlannedSkill]:
    groups: dict[str, list[SourceReplica]] = defaultdict(list)
    for replica in replicas:
        groups[replica.record.skill_sha256].append(replica)
    preliminary = [
        _preliminary_skill(skill_hash, groups[skill_hash])
        for skill_hash in sorted(groups)
    ]
    _resolve_references(preliminary)
    planned = [item.planned for item in preliminary]

    identifiers = [item.identifier for item in planned]
    names = [normalize_name(str(item.manifest["name"])) for item in planned]
    if len(identifiers) != len(set(identifiers)):
        duplicates = [name for name, count in Counter(identifiers).items() if count > 1]
        raise ImportPlanError(f"duplicate normalized skill IDs: {duplicates}")
    if len(names) != len(set(names)):
        duplicates = [name for name, count in Counter(names).items() if count > 1]
        raise ImportPlanError(f"duplicate normalized skill names: {duplicates}")
    return sorted(planned, key=lambda item: (normalize_name(str(item.manifest["name"])), item.identifier))

