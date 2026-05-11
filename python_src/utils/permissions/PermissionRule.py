from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


PermissionBehavior = Literal["allow", "ask", "deny"]


@dataclass(frozen=True)
class PermissionRule:
    tool: str
    value: str = "*"
    behavior: PermissionBehavior = "ask"
    source: str = "project"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


permissionBehaviorSchema = {"enum": ["allow", "ask", "deny"]}
permissionRuleValueSchema = {
    "type": "object",
    "required": ["tool", "value", "behavior"],
    "properties": {
        "tool": {"type": "string"},
        "value": {"type": "string"},
        "behavior": permissionBehaviorSchema,
        "source": {"type": "string"},
    },
}
