from __future__ import annotations

from typing import Any

from python_src.components.sandbox._shared import normalize_dependency, sandbox_payload


async def SandboxDependenciesTab(*args: Any, **kwargs: Any) -> Any:
    deps = kwargs.get("dependencies") or (args[0] if args else []) or []
    rows = [normalize_dependency(dep, index) for index, dep in enumerate(deps)]
    return sandbox_payload("sandbox_dependencies_tab", dependencies=rows, missing=[dep for dep in rows if not dep["installed"]])


__all__ = ["SandboxDependenciesTab"]
