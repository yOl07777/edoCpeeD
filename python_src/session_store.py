from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SessionState:
    messages: list[dict[str, Any]] = field(default_factory=list)

    def add(self, role: str, content: str) -> dict[str, Any]:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.messages.append(message)
        return message

    def clear(self) -> int:
        count = len(self.messages)
        self.messages.clear()
        return count

    def export_jsonl(self) -> str:
        return "\n".join(json.dumps(message, ensure_ascii=False) for message in self.messages)


SESSION_STATE = SessionState()
