from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CostState:
    input_tokens: int = 0
    output_tokens: int = 0
    total_usd: float = 0.0

    def add(self, *, input_tokens: int = 0, output_tokens: int = 0, total_usd: float = 0.0) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_usd += total_usd

    def reset(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_usd = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "total_usd": round(self.total_usd, 8),
        }


COST_STATE = CostState()
