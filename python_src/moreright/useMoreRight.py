"""
External-build shim for ``src/moreright/useMoreRight.tsx``.

The upstream file is intentionally a no-op outside Anthropic's internal build.
This Python port preserves the same public shape: callers receive three async
callbacks and a render function, all of which are safe to call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable


@dataclass
class MoreRightHooks:
    """Callable hook object matching the TypeScript return contract."""

    enabled: bool = False

    async def onBeforeQuery(
        self, input: str = "", all: Iterable[Any] | None = None, n: int = 0
    ) -> bool:
        return True

    async def onTurnComplete(
        self, all: Iterable[Any] | None = None, aborted: bool = False
    ) -> None:
        return None

    def render(self) -> None:
        return None

    def as_dict(self) -> dict[str, Callable[..., Any] | Callable[..., Awaitable[Any]]]:
        return {
            "onBeforeQuery": self.onBeforeQuery,
            "onTurnComplete": self.onTurnComplete,
            "render": self.render,
        }


def useMoreRight(args: dict[str, Any] | None = None, **kwargs: Any) -> MoreRightHooks:
    """Return no-op MoreRight callbacks.

    ``args`` mirrors the TS hook input object; values are accepted for API
    compatibility but the external implementation does not mutate messages,
    input state, or JSX/tool state.
    """

    merged = dict(args or {})
    merged.update(kwargs)
    return MoreRightHooks(enabled=bool(merged.get("enabled", False)))


__all__ = ["MoreRightHooks", "useMoreRight"]
