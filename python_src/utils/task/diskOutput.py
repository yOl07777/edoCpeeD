from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any


DEFAULT_MAX_READ_BYTES = 8 * 1024 * 1024
MAX_TASK_OUTPUT_BYTES = 5 * 1024 * 1024 * 1024
MAX_TASK_OUTPUT_BYTES_DISPLAY = "5GB"

_task_output_dir: Path | None = None
_outputs: dict[str, "DiskTaskOutput"] = {}


def _session_id() -> str:
    try:
        from python_src.bootstrap import state

        return str(state.peekState("sessionId") or "default")
    except Exception:
        return "default"


def getTaskOutputDir() -> str:
    global _task_output_dir
    if _task_output_dir is None:
        _task_output_dir = Path.cwd().resolve() / ".deepseek_tmp" / _session_id() / "tasks"
    _task_output_dir.mkdir(parents=True, exist_ok=True)
    return str(_task_output_dir)


def _resetTaskOutputDirForTest(path: str | os.PathLike[str] | None = None) -> None:
    global _task_output_dir
    _task_output_dir = Path(path).resolve() if path is not None else None


def getTaskOutputPath(taskId: str) -> str:
    return str(Path(getTaskOutputDir()) / f"{taskId}.output")


class DiskTaskOutput:
    def __init__(self, taskId: str) -> None:
        self.task_id = taskId
        self.path = Path(getTaskOutputPath(taskId))
        self._queue: list[str] = []
        self._bytes_written = 0
        self._capped = False
        self._lock = asyncio.Lock()

    def append(self, content: str) -> None:
        if self._capped:
            return
        self._bytes_written += len(content.encode("utf-8", errors="replace"))
        if self._bytes_written > MAX_TASK_OUTPUT_BYTES:
            self._capped = True
            self._queue.append(f"\n[output truncated: exceeded {MAX_TASK_OUTPUT_BYTES_DISPLAY} disk cap]\n")
        else:
            self._queue.append(str(content))

    async def flush(self) -> None:
        async with self._lock:
            if not self._queue:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = "".join(self._queue)
            self._queue.clear()
            with self.path.open("ab") as handle:
                handle.write(data.encode("utf-8", errors="replace"))

    def cancel(self) -> None:
        self._queue.clear()


def _get_or_create_output(taskId: str) -> DiskTaskOutput:
    output = _outputs.get(taskId)
    if output is None:
        output = DiskTaskOutput(taskId)
        _outputs[taskId] = output
    return output


def appendTaskOutput(taskId: str, content: str) -> None:
    _get_or_create_output(taskId).append(content)


async def flushTaskOutput(taskId: str) -> None:
    output = _outputs.get(taskId)
    if output is not None:
        await output.flush()


async def evictTaskOutput(taskId: str) -> None:
    await flushTaskOutput(taskId)
    _outputs.pop(taskId, None)


async def _clearOutputsForTest() -> None:
    for output in _outputs.values():
        output.cancel()
    _outputs.clear()


async def getTaskOutputDelta(
    taskId: str,
    fromOffset: int,
    maxBytes: int = DEFAULT_MAX_READ_BYTES,
) -> dict[str, Any]:
    await flushTaskOutput(taskId)
    path = Path(getTaskOutputPath(taskId))
    if not path.exists():
        return {"content": "", "newOffset": fromOffset}
    with path.open("rb") as handle:
        handle.seek(max(0, fromOffset))
        raw = handle.read(maxBytes)
    return {
        "content": raw.decode("utf-8", errors="replace"),
        "newOffset": fromOffset + len(raw),
    }


async def getTaskOutput(taskId: str, maxBytes: int = DEFAULT_MAX_READ_BYTES) -> str:
    await flushTaskOutput(taskId)
    path = Path(getTaskOutputPath(taskId))
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size > maxBytes:
            handle.seek(size - maxBytes)
        raw = handle.read(maxBytes)
    content = raw.decode("utf-8", errors="replace")
    if size > len(raw):
        omitted = round((size - len(raw)) / 1024)
        return f"[{omitted}KB of earlier output omitted]\n{content}"
    return content


async def getTaskOutputSize(taskId: str) -> int:
    await flushTaskOutput(taskId)
    path = Path(getTaskOutputPath(taskId))
    return path.stat().st_size if path.exists() else 0


async def cleanupTaskOutput(taskId: str) -> None:
    output = _outputs.pop(taskId, None)
    if output is not None:
        output.cancel()
    path = Path(getTaskOutputPath(taskId))
    try:
        path.unlink()
    except FileNotFoundError:
        pass


async def initTaskOutput(taskId: str) -> str:
    path = Path(getTaskOutputPath(taskId))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=False)
    return str(path)


async def initTaskOutputAsSymlink(taskId: str, targetPath: str) -> str:
    output_path = Path(getTaskOutputPath(taskId))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if output_path.exists() or output_path.is_symlink():
            output_path.unlink()
        output_path.symlink_to(Path(targetPath))
    except OSError:
        if not output_path.exists():
            shutil.copyfile(targetPath, output_path)
    return str(output_path)
