from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanState:
    active: bool = False
    goal: str = ""
    steps: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"active": self.active, "goal": self.goal, "steps": list(self.steps)}


PLAN_STATE = PlanState()


def enter_plan(goal: str, steps: list[dict[str, str]] | None = None) -> PlanState:
    PLAN_STATE.active = True
    PLAN_STATE.goal = goal
    PLAN_STATE.steps = steps or []
    return PLAN_STATE


def exit_plan() -> PlanState:
    PLAN_STATE.active = False
    return PLAN_STATE
