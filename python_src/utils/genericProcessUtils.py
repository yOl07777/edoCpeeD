"""Portable process helpers."""

from __future__ import annotations

import os
import platform
import subprocess
from typing import Any


def isProcessRunning(pid: int | str, *_: Any, **__: Any) -> bool:
    try:
        value = int(pid)
    except (TypeError, ValueError):
        return False
    if value <= 1:
        return False
    if value == os.getpid():
        return True
    try:
        os.kill(value, 0)
        return True
    except PermissionError:
        return False
    except OSError:
        return False


def _run(args: list[str], timeout: float = 3.0) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except Exception:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


async def getProcessCommand(pid: int | str, *_: Any, **__: Any) -> str | None:
    pid_s = str(pid)
    if platform.system().lower() == "windows":
        script = f"(Get-CimInstance Win32_Process -Filter \"ProcessId={pid_s}\" -ErrorAction SilentlyContinue).CommandLine"
        out = _run(["powershell.exe", "-NoProfile", "-Command", script], timeout=2.0)
    else:
        out = _run(["ps", "-o", "command=", "-p", pid_s], timeout=2.0)
    return out or None


async def getAncestorPidsAsync(pid: int | str, maxDepth: int = 10, *_: Any, **__: Any) -> list[int]:
    current = str(pid)
    result: list[int] = []
    for _depth in range(maxDepth):
        if platform.system().lower() == "windows":
            script = f"(Get-CimInstance Win32_Process -Filter \"ProcessId={current}\" -ErrorAction SilentlyContinue).ParentProcessId"
            out = _run(["powershell.exe", "-NoProfile", "-Command", script])
        else:
            out = _run(["ps", "-o", "ppid=", "-p", current])
        try:
            parent = int(out.strip())
        except (TypeError, ValueError):
            break
        if parent <= 1:
            break
        result.append(parent)
        current = str(parent)
    return result


async def getAncestorCommandsAsync(pid: int | str, maxDepth: int = 10, *_: Any, **__: Any) -> list[str]:
    pids = [int(pid)] if str(pid).isdigit() else []
    pids.extend(await getAncestorPidsAsync(pid, maxDepth=maxDepth))
    commands: list[str] = []
    for item in pids[:maxDepth]:
        command = await getProcessCommand(item)
        if command:
            commands.append(command)
    return commands


async def getChildPids(pid: int | str, *_: Any, **__: Any) -> list[int]:
    pid_s = str(pid)
    if platform.system().lower() == "windows":
        script = f"(Get-CimInstance Win32_Process -Filter \"ParentProcessId={pid_s}\" -ErrorAction SilentlyContinue).ProcessId"
        out = _run(["powershell.exe", "-NoProfile", "-Command", script])
        parts = out.split()
    else:
        out = _run(["pgrep", "-P", pid_s], timeout=2.0)
        parts = out.splitlines()
    result: list[int] = []
    for part in parts:
        try:
            result.append(int(part.strip()))
        except ValueError:
            pass
    return result


__all__ = [
    "getAncestorCommandsAsync",
    "getAncestorPidsAsync",
    "getChildPids",
    "getProcessCommand",
    "isProcessRunning",
]
