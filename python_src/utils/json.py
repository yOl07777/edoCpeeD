from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from python_src.utils.jsonRead import stripBOM


def _strip_jsonc_comments(text: str) -> str:
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def safeParseJSON(json_text: str | None, shouldLogError: bool = True) -> Any:
    if not json_text:
        return None
    try:
        return json.loads(stripBOM(json_text))
    except Exception:
        return None


safeParseJSON.cache = {}  # type: ignore[attr-defined]


def safeParseJSONC(json_text: str | None) -> Any:
    if not json_text:
        return None
    try:
        return json.loads(_strip_jsonc_comments(stripBOM(json_text)))
    except Exception:
        return None


def parseJSONL(data: str | bytes) -> list[Any]:
    text = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
    text = stripBOM(text)
    out: list[Any] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


async def readJSONLFile(filePath: str) -> list[Any]:
    path = Path(filePath)
    if not path.exists():
        return []
    max_bytes = 100 * 1024 * 1024
    data = path.read_bytes()
    if len(data) > max_bytes:
        data = data[-max_bytes:]
        newline = data.find(b"\n")
        if newline != -1:
            data = data[newline + 1 :]
    return parseJSONL(data)


def addItemToJSONCArray(content: str, newItem: Any) -> str:
    parsed = safeParseJSONC(content)
    if not isinstance(parsed, list):
        parsed = []
    parsed.append(newItem)
    return json.dumps(parsed, ensure_ascii=False, indent=4)
