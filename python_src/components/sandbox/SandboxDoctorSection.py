from __future__ import annotations

from typing import Any

from python_src.components.sandbox._shared import sandbox_payload


async def SandboxDoctorSection(*args: Any, **kwargs: Any) -> Any:
    checks = kwargs.get("checks") or (args[0] if args else []) or []
    rows = [check if isinstance(check, dict) else {"name": str(check), "ok": True} for check in checks]
    return sandbox_payload("sandbox_doctor_section", checks=rows, ok=all(bool(row.get("ok", False)) for row in rows) if rows else True)


__all__ = ["SandboxDoctorSection"]
