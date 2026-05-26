from __future__ import annotations

import hashlib


def djb2Hash(str: str) -> int:
    value = 0
    for ch in str:
        value = ((value << 5) - value + ord(ch)) & 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def hashContent(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def hashPair(a: str, b: str) -> str:
    h = hashlib.sha256()
    h.update(a.encode("utf-8"))
    h.update(b"\0")
    h.update(b.encode("utf-8"))
    return h.hexdigest()
