from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any


class Dirent:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = path.name

    def isFile(self) -> bool:
        return self.path.is_file()

    def isDirectory(self) -> bool:
        return self.path.is_dir()

    def isSymbolicLink(self) -> bool:
        return self.path.is_symlink()


class NodeFsOperations:
    def cwd(self) -> str:
        return os.getcwd()

    def existsSync(self, path: str) -> bool:
        return Path(path).exists()

    async def stat(self, path: str) -> os.stat_result:
        return Path(path).stat()

    def statSync(self, path: str) -> os.stat_result:
        return Path(path).stat()

    def lstatSync(self, path: str) -> os.stat_result:
        return Path(path).lstat()

    async def readdir(self, path: str) -> list[Dirent]:
        return [Dirent(p) for p in Path(path).iterdir()]

    def readdirSync(self, path: str) -> list[Dirent]:
        return [Dirent(p) for p in Path(path).iterdir()]

    def readdirStringSync(self, path: str) -> list[str]:
        return [p.name for p in Path(path).iterdir()]

    async def unlink(self, path: str) -> None:
        Path(path).unlink()

    def unlinkSync(self, path: str) -> None:
        Path(path).unlink()

    async def rmdir(self, path: str) -> None:
        Path(path).rmdir()

    def rmdirSync(self, path: str) -> None:
        Path(path).rmdir()

    async def rm(self, path: str, options: dict[str, Any] | None = None) -> None:
        self.rmSync(path, options)

    def rmSync(self, path: str, options: dict[str, Any] | None = None) -> None:
        p = Path(path)
        force = bool((options or {}).get("force"))
        recursive = bool((options or {}).get("recursive"))
        try:
            if p.is_dir() and not p.is_symlink():
                shutil.rmtree(p) if recursive else p.rmdir()
            else:
                p.unlink()
        except FileNotFoundError:
            if not force:
                raise

    async def mkdir(self, path: str, options: dict[str, Any] | None = None) -> None:
        Path(path).mkdir(parents=True, exist_ok=True, mode=int((options or {}).get("mode", 0o777)))

    def mkdirSync(self, path: str, options: dict[str, Any] | None = None) -> None:
        Path(path).mkdir(parents=True, exist_ok=True, mode=int((options or {}).get("mode", 0o777)))

    async def readFile(self, path: str, options: dict[str, Any] | None = None) -> str:
        return Path(path).read_text(encoding=(options or {}).get("encoding", "utf-8"), errors="replace")

    def readFileSync(self, path: str, options: dict[str, Any] | None = None) -> str:
        return Path(path).read_text(encoding=(options or {}).get("encoding", "utf-8"), errors="replace")

    def readFileBytesSync(self, path: str) -> bytes:
        return Path(path).read_bytes()

    async def readFileBytes(self, path: str, maxBytes: int | None = None) -> bytes:
        data = Path(path).read_bytes()
        return data[:maxBytes] if maxBytes is not None else data

    def readSync(self, path: str, options: dict[str, Any]) -> dict[str, Any]:
        data = Path(path).read_bytes()[: int(options.get("length", 4096))]
        return {"buffer": data, "bytesRead": len(data)}

    def appendFileSync(self, path: str, data: str, options: dict[str, Any] | None = None) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("a", encoding="utf-8") as handle:
            handle.write(data)

    def copyFileSync(self, src: str, dest: str) -> None:
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    async def rename(self, oldPath: str, newPath: str) -> None:
        Path(oldPath).rename(newPath)

    def renameSync(self, oldPath: str, newPath: str) -> None:
        Path(oldPath).rename(newPath)

    def linkSync(self, target: str, path: str) -> None:
        os.link(target, path)

    def symlinkSync(self, target: str, path: str, type: str | None = None) -> None:
        os.symlink(target, path, target_is_directory=type in {"dir", "junction"})

    def readlinkSync(self, path: str) -> str:
        return os.readlink(path)

    def realpathSync(self, path: str) -> str:
        return str(Path(path).resolve(strict=True))

    def isDirEmptySync(self, path: str) -> bool:
        return not any(Path(path).iterdir())

    def createWriteStream(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return Path(path).open("wb")


_original = NodeFsOperations()
_current: Any = _original


def getFsImplementation() -> Any:
    return _current


def setFsImplementation(fs: Any) -> Any:
    global _current
    old = _current
    _current = fs
    return old


def setOriginalFsImplementation() -> None:
    global _current
    _current = _original


def safeResolvePath(fs: Any, filePath: str) -> dict[str, Any]:
    if filePath.startswith("//") or filePath.startswith("\\\\"):
        return {"resolvedPath": filePath, "isSymlink": False, "isCanonical": False}
    try:
        resolved = fs.realpathSync(filePath)
        return {"resolvedPath": resolved, "isSymlink": os.path.abspath(filePath) != resolved, "isCanonical": True}
    except Exception:
        return {"resolvedPath": filePath, "isSymlink": False, "isCanonical": False}


def isDuplicatePath(fs: Any, filePath: str, loadedPaths: set[str]) -> bool:
    resolved = safeResolvePath(fs, filePath)["resolvedPath"]
    if resolved in loadedPaths:
        return True
    loadedPaths.add(resolved)
    return False


def resolveDeepestExistingAncestorSync(fs: Any, absolutePath: str) -> str | None:
    path = Path(absolutePath)
    tail: list[str] = []
    while not path.exists() and path.parent != path:
        tail.insert(0, path.name)
        path = path.parent
    if not path.exists():
        return None
    try:
        resolved = Path(fs.realpathSync(str(path)))
    except Exception:
        return None
    return str(resolved.joinpath(*tail))


async def readFileRange(filePath: str, fromOffset: int, maxBytes: int) -> dict[str, Any] | None:
    path = Path(filePath)
    if not path.exists():
        return None
    with path.open("rb") as handle:
        handle.seek(max(0, fromOffset))
        data = handle.read(maxBytes)
    return {"content": data.decode("utf-8", errors="replace"), "bytesRead": len(data)}


async def tailFile(filePath: str, maxBytes: int) -> dict[str, Any]:
    data = Path(filePath).read_bytes()
    tail = data[-maxBytes:]
    return {"content": tail.decode("utf-8", errors="replace"), "bytesTotal": len(data), "bytesRead": len(tail)}


def getPathsForPermissionCheck(path: str) -> list[str]:
    resolved = safeResolvePath(_current, path)["resolvedPath"]
    return [path] if resolved == path else [path, resolved]
