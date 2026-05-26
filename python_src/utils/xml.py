from __future__ import annotations


def escapeXml(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escapeXmlAttr(s: str) -> str:
    return escapeXml(s).replace('"', "&quot;").replace("'", "&apos;")
