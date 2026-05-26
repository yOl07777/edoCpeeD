"""Feedback command shim for the Python migration."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


def renderFeedbackComponent(
    onDone: DoneCallback | None,
    abortSignal: Any = None,
    messages: list[dict[str, Any]] | None = None,
    initialDescription: str = "",
    backgroundTasks: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": "feedback",
        "initialDescription": initialDescription,
        "messages": list(messages or []),
        "backgroundTasks": dict(backgroundTasks or {}),
        "abortSignal": abortSignal,
        "onDone": onDone,
    }


async def call(onDone: DoneCallback | None = None, context: dict[str, Any] | Any = None, args: str | None = None) -> dict[str, Any]:
    initial = args or ""
    if isinstance(context, dict):
        controller = context.get("abortController")
        abort_signal = context.get("abortSignal")
        if abort_signal is None and isinstance(controller, dict):
            abort_signal = controller.get("signal")
        messages = context.get("messages", [])
        background_tasks = context.get("backgroundTasks", {})
    else:
        controller = getattr(context, "abortController", None)
        abort_signal = getattr(controller, "signal", None)
        messages = getattr(context, "messages", [])
        background_tasks = getattr(context, "backgroundTasks", {})
    return renderFeedbackComponent(onDone, abort_signal, messages, initial, background_tasks)
