from __future__ import annotations


UTF8_BOM = "\ufeff"


def stripBOM(content: str) -> str:
    return content[1:] if isinstance(content, str) and content.startswith(UTF8_BOM) else content
