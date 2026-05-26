from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload


class SentryErrorBoundary:
    """Local error boundary shim that stores render errors without remote reporting."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self.error: Any = None

    def capture(self, error: Any) -> dict[str, Any]:
        self.error = error
        return component_payload("sentry_error_boundary", captured=True, error=str(error), remoteReported=False)

    def render(self, child: Any = None) -> dict[str, Any]:
        return component_payload("sentry_error_boundary_render", child=child, error=str(self.error) if self.error else None)


__all__ = ["SentryErrorBoundary"]
