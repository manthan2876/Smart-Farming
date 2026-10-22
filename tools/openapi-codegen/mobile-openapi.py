from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


MOBILE_OPERATIONS = {
    "/api/v1/alerts": {"get"},
    "/api/v1/alerts/{alert_id}/read": {"post"},
    "/api/v1/auth/change-password": {"post"},
    "/api/v1/auth/forgot-password": {"post"},
    "/api/v1/auth/guest": {"post"},
    "/api/v1/auth/login": {"post"},
    "/api/v1/auth/refresh": {"post"},
    "/api/v1/auth/register": {"post"},
    "/api/v1/auth/reset-password": {"post"},
    "/api/v1/crops": {"get"},
    "/api/v1/farm": {"get", "put"},
    "/api/v1/farm/plots": {"post"},
    "/api/v1/farm/plots/{plot_id}": {"put", "delete"},
    "/api/v1/feedback": {"post"},
    "/api/v1/history": {"get"},
    "/api/v1/predict": {"post"},
    "/api/v1/predictions/{prediction_id}": {"get"},
    "/api/v1/predictions/{prediction_id}/request-expert": {"post"},
    "/api/v1/predictions/{prediction_id}/rescan": {"post"},
    "/api/v1/predictions/{prediction_id}/translate": {"post"},
    "/api/v1/profile": {"get", "patch"},
    "/api/v1/tts": {"post"},
    "/api/v1/weather": {"get"},
    "/api/v1/weather/translate": {"post"},
}


def schema_references(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            refs.add(ref.rsplit("/", 1)[-1])
        for child in value.values():
            refs.update(schema_references(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(schema_references(child))
    return refs


def main() -> None:
    source, destination = map(Path, sys.argv[1:3])
    spec = json.loads(source.read_text(encoding="utf-8"))
    missing = {
        path: sorted(methods)
        for path, methods in MOBILE_OPERATIONS.items()
        if path not in spec["paths"]
        or not methods.issubset({method.lower() for method in spec["paths"][path]})
    }
    if missing:
        raise SystemExit(f"OpenAPI is missing mobile operations: {missing}")

    selected_paths: dict[str, dict[str, Any]] = {}
    roots: set[str] = set()
    for path, operations in MOBILE_OPERATIONS.items():
        path_item = spec["paths"][path]
        selected_item = {
            key: value
            for key, value in path_item.items()
            if key.lower() not in {
                "get", "post", "put", "patch", "delete",
                "options", "head", "trace",
            }
        }
        for method in operations:
            operation = dict(path_item[method])
            operation.get("responses", {}).pop("422", None)
            selected_item[method] = operation
            roots.update(schema_references(operation))
            roots.update(schema_references(selected_item))
        selected_paths[path] = selected_item

    schemas = spec.get("components", {}).get("schemas", {})
    included: dict[str, Any] = {}
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in included or name not in schemas:
            continue
        schema = schemas[name]
        included[name] = schema
        pending.extend(schema_references(schema) - included.keys())

    # The Dart generator emits invalid code for a map/string union. The mobile
    # API normalizes prediction statuses to structured status objects.
    prediction_schema = included.get("PredictionResponse")
    if prediction_schema:
        status_schema = prediction_schema.get("properties", {}).get("status")
        if status_schema:
            status_schema["anyOf"] = [
                {"$ref": "#/components/schemas/PredictionStatusResponse"},
                {"type": "null"},
            ]

    spec["paths"] = selected_paths
    components = spec.get("components", {})
    spec["components"] = {
        **({"securitySchemes": components["securitySchemes"]} if "securitySchemes" in components else {}),
        "schemas": included,
    }
    destination.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
