from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

from python_src.utils.fileRead import detectEncodingForResolvedPath


class FileReadCache:
    def __init__(self, maxCacheSize: int = 1000) -> None:
        self.cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.maxCacheSize = maxCacheSize

    def readFile(self, filePath: str) -> dict[str, str]:
        path = Path(filePath)
        mtime = path.stat().st_mtime_ns
        cached = self.cache.get(str(path))
        if cached and cached["mtime"] == mtime:
            self.cache.move_to_end(str(path))
            return {"content": cached["content"], "encoding": cached["encoding"]}
        encoding = detectEncodingForResolvedPath(str(path))
        content = path.read_text(encoding=encoding, errors="replace").replace("\r\n", "\n")
        self.cache[str(path)] = {"content": content, "encoding": encoding, "mtime": mtime}
        self.cache.move_to_end(str(path))
        while len(self.cache) > self.maxCacheSize:
            self.cache.popitem(last=False)
        return {"content": content, "encoding": encoding}

    def clear(self) -> None:
        self.cache.clear()

    def invalidate(self, filePath: str) -> None:
        self.cache.pop(str(Path(filePath)), None)

    def getStats(self) -> dict[str, Any]:
        return {"size": len(self.cache), "entries": list(self.cache.keys())}


fileReadCache = FileReadCache()
