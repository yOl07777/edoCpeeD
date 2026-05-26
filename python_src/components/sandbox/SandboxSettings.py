from __future__ import annotations

from typing import Any

from python_src.components.sandbox.SandboxConfigTab import SandboxConfigTab
from python_src.components.sandbox.SandboxDependenciesTab import SandboxDependenciesTab
from python_src.components.sandbox.SandboxDoctorSection import SandboxDoctorSection
from python_src.components.sandbox.SandboxOverridesTab import SandboxOverridesTab
from python_src.components.sandbox._shared import sandbox_payload


async def SandboxSettings(*args: Any, **kwargs: Any) -> Any:
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    return sandbox_payload(
        "sandbox_settings",
        configTab=await SandboxConfigTab(config),
        dependenciesTab=await SandboxDependenciesTab(kwargs.get("dependencies", [])),
        doctorSection=await SandboxDoctorSection(kwargs.get("checks", [])),
        overridesTab=await SandboxOverridesTab(kwargs.get("overrides", [])),
    )


__all__ = ["SandboxSettings"]
