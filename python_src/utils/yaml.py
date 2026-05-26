from __future__ import annotations

import json
from typing import Any


def parseYaml(input: str) -> Any:
    try:
        import yaml as pyyaml  # type: ignore

        return pyyaml.safe_load(input)
    except Exception:
        text = input.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            result: dict[str, Any] = {}
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or ":" not in stripped:
                    continue
                key, value = stripped.split(":", 1)
                value = value.strip()
                if value.lower() in {"true", "false"}:
                    parsed: Any = value.lower() == "true"
                elif value == "":
                    parsed = None
                else:
                    try:
                        parsed = int(value)
                    except ValueError:
                        parsed = value.strip('"\'')
                result[key.strip()] = parsed
            return result
