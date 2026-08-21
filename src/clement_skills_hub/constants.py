"""Shared immutable values for P0-01."""

from __future__ import annotations

GENERATOR_VERSION = "0.1.0"
REGISTRY_VERSION = "1.0.0"
MANIFEST_SCHEMA_VERSION = "1.0.0"

VALID_STATUSES = frozenset(
    {
        "ACTIVE",
        "CANDIDATE",
        "NEEDS_REVIEW",
        "DEPRECATED",
        "ARCHIVED",
        "CONFLICT",
        "INCOMPLETE",
    }
)

VALID_CATEGORIES = (
    "coding",
    "documents",
    "research",
    "3d",
    "blender",
    "unreal",
    "comfyui",
    "filesystem",
    "github",
    "orchestration",
    "security",
    "other",
)

REQUIRED_INVENTORY_COLUMNS = frozenset(
    {
        "SkillName",
        "NormalizedName",
        "NameSource",
        "RootPath",
        "HasSkill",
        "SkillPath",
        "SkillSha256",
        "HasManifest",
        "ManifestPath",
        "ManifestSha256",
        "ManifestValid",
        "ManifestNamePresent",
        "ManifestError",
        "AuditStatus",
    }
)

CATEGORY_KEYWORDS: tuple[tuple[str, frozenset[str]], ...] = (
    ("blender", frozenset({"blender", "bpy", "geometry-nodes"})),
    ("unreal", frozenset({"unreal", "ue5", "nanite", "lumen"})),
    ("comfyui", frozenset({"comfyui", "stable-diffusion", "workflow-image"})),
    ("github", frozenset({"github", "git", "pull-request", "gitops"})),
    ("security", frozenset({"security", "secure", "audit", "red-team", "blue-team", "threat"})),
    ("filesystem", frozenset({"filesystem", "file", "folder", "directory", "powershell"})),
    ("orchestration", frozenset({"orchestration", "orchestrator", "agent", "coalition", "routing"})),
    ("documents", frozenset({"document", "docx", "pdf", "spreadsheet", "excel", "slides", "presentation"})),
    ("research", frozenset({"research", "search", "citation", "literature", "paper"})),
    ("3d", frozenset({"3d", "modeling", "mesh", "render", "asset", "landscape"})),
    ("coding", frozenset({"coding", "code", "python", "javascript", "typescript", "programming", "developer"})),
)

