"""Console/logger helpers for the Python bridge runtime."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, TextIO


@dataclass(slots=True)
class BridgeLogEvent:
    level: str
    message: str
    timestamp: float = field(default_factory=time.time)
    data: dict[str, Any] | None = None


class BridgeConsoleLogger:
    """Small bridge logger compatible with the TS logger surface."""

    def __init__(
        self,
        *,
        stream: TextIO | None = None,
        verbose: bool = False,
        quiet: bool = False,
        on_event: Callable[[BridgeLogEvent], Any] | None = None,
    ) -> None:
        self.stream = stream or sys.stderr
        self.verbose = verbose
        self.quiet = quiet
        self.on_event = on_event
        self.events: list[BridgeLogEvent] = []
        self.status = "idle"
        self.session_titles: dict[str, str] = {}

    def _record(self, level: str, message: str, data: dict[str, Any] | None = None) -> None:
        event = BridgeLogEvent(level=level, message=str(message), data=data)
        self.events.append(event)
        if self.on_event:
            self.on_event(event)
        if not self.quiet and (level != "debug" or self.verbose):
            print(f"[bridge:{level}] {event.message}", file=self.stream)

    def debug(self, message: str, *args: Any) -> None:
        self._record("debug", message.format(*args) if args else message)

    def info(self, message: str, *args: Any) -> None:
        self._record("info", message.format(*args) if args else message)

    def warn(self, message: str, *args: Any) -> None:
        self._record("warn", message.format(*args) if args else message)

    def error(self, message: str, *args: Any) -> None:
        self._record("error", message.format(*args) if args else message)

    def log(self, message: str) -> None:
        self.info(message)

    def logVerbose(self, message: str) -> None:
        self.debug(message)

    def logError(self, message: str) -> None:
        self.error(message)

    def setStatus(self, status: str, **data: Any) -> None:
        self.status = status
        self._record("status", status, data or None)

    def updateIdleStatus(self, **data: Any) -> None:
        self.setStatus("idle", **data)

    def updateActiveStatus(self, **data: Any) -> None:
        self.setStatus("active", **data)

    def updateFailedStatus(self, message: str = "failed", **data: Any) -> None:
        self.status = "failed"
        self._record("error", message, data or None)

    def setSessionTitle(self, session_id: str, title: str) -> None:
        self.session_titles[session_id] = title
        self._record("session_title", f"{session_id}: {title}")

    def close(self) -> None:
        self._record("debug", "closed")

    def __getattr__(self, name: str) -> Callable[..., None]:
        def recorder(*args: Any, **kwargs: Any) -> None:
            message = " ".join(str(arg) for arg in args) if args else name
            self._record(name, message, kwargs or None)

        return recorder


def createBridgeLogger(options: dict[str, Any] | None = None, **kwargs: Any) -> BridgeConsoleLogger:
    opts = {**(options or {}), **kwargs}
    return BridgeConsoleLogger(
        stream=opts.get("stream"),
        verbose=bool(opts.get("verbose") or opts.get("debug")),
        quiet=bool(opts.get("quiet")),
        on_event=opts.get("on_event") or opts.get("onEvent"),
    )
