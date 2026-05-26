"""FileEditTool schema compatibility constants."""

from __future__ import annotations

hunkSchema = {
    "type": "object",
    "properties": {
        "oldStart": {"type": "integer"},
        "oldLines": {"type": "integer"},
        "newStart": {"type": "integer"},
        "newLines": {"type": "integer"},
        "lines": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["lines"],
    "additionalProperties": True,
}

gitDiffSchema = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "oldPath": {"type": "string"},
        "newPath": {"type": "string"},
        "hunks": {"type": "array", "items": hunkSchema},
    },
    "required": ["hunks"],
    "additionalProperties": True,
}

__all__ = ["gitDiffSchema", "hunkSchema"]
