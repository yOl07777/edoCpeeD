from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PermissionContext:
    tool_name: str
    input: Any = None
    cwd: str | None = None
    mode: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def createPermissionContext(
    tool_name: str,
    input: Any = None,
    *,
    cwd: str | None = None,
    mode: str = "default",
    metadata: dict[str, Any] | None = None,
) -> PermissionContext:
    return PermissionContext(tool_name=tool_name, input=input, cwd=cwd, mode=mode, metadata=metadata or {})
