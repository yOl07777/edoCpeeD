"""PowerShell command result interpretation helpers."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _first_line(value: Any) -> str:
    text = str(value or "").strip()
    return text.splitlines()[0] if text else ""


async def interpretCommandResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    timed_out = bool(data.get("timed_out") or data.get("timedOut", False))
    exit_code = int(data.get("exit_code", data.get("exitCode", 0)) or 0)
    stdout = str(data.get("stdout", ""))
    stderr = str(data.get("stderr", ""))
    if timed_out:
        status = "timed_out"
        summary = _first_line(stderr) or "PowerShell command timed out"
    elif exit_code == 0:
        status = "success"
        summary = _first_line(stdout) or "PowerShell command completed"
    else:
        status = "failed"
        summary = _first_line(stderr) or _first_line(stdout) or f"PowerShell exited with code {exit_code}"
    return {
        "status": status,
        "exitCode": exit_code,
        "timedOut": timed_out,
        "summary": summary,
        "stdout": stdout,
        "stderr": stderr,
    }


__all__ = ["interpretCommandResult"]
