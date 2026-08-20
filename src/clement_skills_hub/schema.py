"""Small strict validator for the JSON Schema subset used by this Hub.

The project deliberately avoids a runtime dependency. The supported subset is
validated by unit tests and covers every keyword present in both repository
schemas: type, required, properties, additionalProperties, items, enum, const,
pattern, minLength, minimum, minItems and uniqueItems.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import RepositoryValidationError


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RepositoryValidationError(f"invalid JSON file {path}: {exc}") from exc


def _matches_type(instance: Any, expected: str) -> bool:
    if expected == "null":
        return instance is None
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    return False


def validate_schema(instance: Any, schema: dict[str, Any], *, path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = [expected_type] if isinstance(expected_type, str) else list(expected_type)
        if not any(_matches_type(instance, item) for item in expected_types):
            errors.append(f"{path}: expected type {expected_types}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not in enum")

    if isinstance(instance, str):
        minimum_length = schema.get("minLength")
        if minimum_length is not None and len(instance) < int(minimum_length):
            errors.append(f"{path}: string is shorter than {minimum_length}")
        pattern = schema.get("pattern")
        if pattern is not None and re.search(str(pattern), instance) is None:
            errors.append(f"{path}: string does not match {pattern!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            errors.append(f"{path}: value is below minimum {minimum}")

    if isinstance(instance, list):
        minimum_items = schema.get("minItems")
        if minimum_items is not None and len(instance) < int(minimum_items):
            errors.append(f"{path}: array has fewer than {minimum_items} items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, item_schema, path=f"{path}[{index}]"))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, value in instance.items():
                property_schema = properties.get(key)
                if isinstance(property_schema, dict):
                    errors.extend(validate_schema(value, property_schema, path=f"{path}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property {key!r}")
    return errors


def assert_valid_schema(instance: Any, schema: dict[str, Any], *, label: str) -> None:
    errors = validate_schema(instance, schema)
    if errors:
        preview = "; ".join(errors[:20])
        suffix = f"; ... {len(errors) - 20} more" if len(errors) > 20 else ""
        raise RepositoryValidationError(f"{label} schema validation failed: {preview}{suffix}")


def validate_schema_document(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    supported = {
        "$schema",
        "$id",
        "title",
        "type",
        "required",
        "properties",
        "additionalProperties",
        "items",
        "enum",
        "const",
        "pattern",
        "minLength",
        "minimum",
        "minItems",
        "uniqueItems",
    }

    def visit(node: object, path: str) -> None:
        if not isinstance(node, dict):
            errors.append(f"{path}: schema node must be an object")
            return
        unknown = sorted(set(node) - supported)
        if unknown:
            errors.append(f"{path}: unsupported schema keywords: {unknown}")
        properties = node.get("properties")
        if isinstance(properties, dict):
            for key, value in properties.items():
                visit(value, f"{path}.properties.{key}")
        items = node.get("items")
        if isinstance(items, dict):
            visit(items, f"{path}.items")

    visit(schema, "$")
    return errors

