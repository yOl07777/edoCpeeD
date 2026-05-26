from __future__ import annotations

from copy import deepcopy
from typing import Any


def zodToJsonSchema(schema: Any) -> dict[str, Any]:
    if isinstance(schema, dict):
        return deepcopy(schema)
    if hasattr(schema, "to_json_schema"):
        result = schema.to_json_schema()
        return dict(result)
    if hasattr(schema, "model_json_schema"):
        return dict(schema.model_json_schema())
    if hasattr(schema, "schema"):
        result = schema.schema()
        if isinstance(result, dict):
            return dict(result)
    return {"type": "object", "additionalProperties": True}
