from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from python_src.utils.fileRead import detectEncodingForResolvedPath, detectLineEndingsForString
from python_src.utils.fileReadCache import fileReadCache
from python_src.utils.path import expandPath


MAX_OUTPUT_SIZE = int(0.25 * 1024 * 1024)
FILE_NOT_FOUND_CWD_NOTE = "Note: your current working directory is"


def pathExists(path: str) -> bool:
    return Path(path).exists()


def readFileSafe(filepath: str) -> str | None:
    try:
        return Path(filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def getFileModificationTime(filePath: str) -> int:
    return int(Path(filePath).stat().st_mtime * 1000)


async def getFileModificationTimeAsync(filePath: str) -> int:
    return getFileModificationTime(filePath)


def writeFileSyncAndFlush_DEPRECATED(filePath: str, content: str, options: dict[str, Any] | None = None) -> None:
    path = Path(filePath)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoding = (options or {}).get("encoding", "utf-8")
    path.write_text(content, encoding=encoding)


def writeTextContent(filePath: str, content: str, encoding: str = "utf-8", endings: str = "LF") -> None:
    to_write = content.replace("\r\n", "\n")
    if endings == "CRLF":
        to_write = to_write.replace("\n", "\r\n")
    writeFileSyncAndFlush_DEPRECATED(filePath, to_write, {"encoding": encoding})


def detectFileEncoding(filePath: str) -> str:
    return detectEncodingForResolvedPath(filePath)


def detectLineEndings(filePath: str, encoding: str = "utf-8") -> str:
    try:
        head = Path(filePath).read_text(encoding=encoding, errors="replace")[:4096]
    except Exception:
        return "LF"
    return detectLineEndingsForString(head)


def convertLeadingTabsToSpaces(content: str) -> str:
    return re.sub(r"^\t+", lambda m: "  " * len(m.group(0)), content, flags=re.MULTILINE)


def getAbsoluteAndRelativePaths(path: str | None) -> dict[str, str | None]:
    absolute = expandPath(path) if path else None
    try:
        relative = os.path.relpath(absolute, os.getcwd()) if absolute else None
    except ValueError:
        relative = absolute
    return {"absolutePath": absolute, "relativePath": relative}


def getDisplayPath(filePath: str) -> str:
    paths = getAbsoluteAndRelativePaths(filePath)
    relative = paths["relativePath"]
    if relative and not relative.startswith(".."):
        return relative
    home = str(Path.home())
    absolute = str(filePath)
    if absolute.startswith(home + os.sep):
        return "~" + absolute[len(home) :]
    return absolute


def findSimilarFile(filePath: str) -> str | None:
    path = Path(filePath)
    try:
        for child in path.parent.iterdir():
            if child != path and child.stem == path.stem:
                return child.name
    except Exception:
        return None
    return None


async def suggestPathUnderCwd(requestedPath: str) -> str | None:
    cwd = Path.cwd().resolve()
    requested = Path(requestedPath).resolve(strict=False)
    try:
        rel = requested.relative_to(cwd.parent)
    except ValueError:
        return None
    corrected = cwd / rel
    if corrected.exists() and cwd in corrected.parents:
        return str(corrected)
    return None


def normalizePathForComparison(path: str) -> str:
    normalized = os.path.normcase(os.path.normpath(path))
    return normalized.replace("\\", "/")


def pathsEqual(a: str, b: str) -> bool:
    return normalizePathForComparison(a) == normalizePathForComparison(b)


def isDirEmpty(path: str) -> bool:
    return not any(Path(path).iterdir())


def isFileWithinReadSizeLimit(path: str, maxSizeBytes: int = MAX_OUTPUT_SIZE) -> bool:
    try:
        return Path(path).stat().st_size <= maxSizeBytes
    except FileNotFoundError:
        return False


def addLineNumbers(content: str, startLine: int = 1) -> str:
    return "\n".join(f"{index:>6}\t{line}" for index, line in enumerate(content.splitlines(), start=startLine))


def stripLineNumberPrefix(content: str) -> str:
    return "\n".join(re.sub(r"^\s*\d+\t", "", line) for line in content.splitlines())


def isCompactLinePrefixEnabled(*_args: Any, **_kwargs: Any) -> bool:
    return True


def readFileSyncCached(filePath: str) -> str:
    return fileReadCache.readFile(filePath)["content"]


def getDesktopPath() -> str:
    return str(Path.home() / "Desktop")
