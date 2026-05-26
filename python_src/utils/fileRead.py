from __future__ import annotations

from pathlib import Path
from typing import Literal


LineEndingType = Literal["CRLF", "LF"]


def detectEncodingForResolvedPath(resolvedPath: str) -> str:
    try:
        head = Path(resolvedPath).read_bytes()[:4096]
    except FileNotFoundError:
        return "utf-8"
    if head.startswith(b"\xff\xfe"):
        return "utf-16-le"
    if head.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def detectLineEndingsForString(content: str) -> LineEndingType:
    crlf = content.count("\r\n")
    lf = content.count("\n") - crlf
    return "CRLF" if crlf > lf else "LF"


def readFileSyncWithMetadata(filePath: str) -> dict[str, str]:
    path = Path(filePath)
    encoding = detectEncodingForResolvedPath(str(path))
    raw = path.read_text(encoding=encoding, errors="replace")
    return {
        "content": raw.replace("\r\n", "\n"),
        "encoding": encoding,
        "lineEndings": detectLineEndingsForString(raw[:4096]),
    }


def readFileSync(filePath: str) -> str:
    return readFileSyncWithMetadata(filePath)["content"]
