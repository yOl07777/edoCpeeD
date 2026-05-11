from __future__ import annotations

import re
from typing import Any


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
        value = value.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")
    return value


async def parseGitConfigValue(value: str) -> Any:
    text = _unquote(value)
    lowered = text.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"", "auto"}:
        return text
    if re.fullmatch(r"[+-]?\d+", text):
        try:
            return int(text)
        except ValueError:
            return text
    return text


async def parseConfigString(config: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    section = ""
    subsection = ""
    for raw_line in config.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("[") and line.endswith("]"):
            header = line[1:-1].strip()
            match = re.match(r'([^\s"]+)\s+"(.+)"$', header)
            if match:
                section, subsection = match.group(1), match.group(2)
            else:
                section, subsection = header, ""
            key = f"{section}.{subsection}" if subsection else section
            result.setdefault(key, {})
            continue
        if "=" in line and section:
            key, value = line.split("=", 1)
            bucket = f"{section}.{subsection}" if subsection else section
            result.setdefault(bucket, {})[key.strip()] = await parseGitConfigValue(value)
    return result
