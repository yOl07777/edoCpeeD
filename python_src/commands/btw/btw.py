"""Side-question command used by `/btw`."""

from __future__ import annotations

from inspect import isawaitable
from typing import Any, Awaitable, Callable

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


def buildCacheSafeParams(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract model-call context without carrying provider-specific cache flags."""

    context = context or {}
    messages = []
    for message in context.get("messages", []) or []:
        if not isinstance(message, dict):
            continue
        clean = {key: value for key, value in message.items() if key != "cache_control"}
        messages.append(clean)
    return {
        "messages": messages,
        "model": context.get("model") or context.get("defaultModel"),
        "tools": context.get("tools", []),
        "provider": "deepseek",
    }


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if isawaitable(result):
        await result


async def _run_side_question(context: dict[str, Any], payload: dict[str, Any]) -> Any:
    runner = context.get("sideQuestionRunner") or context.get("processor")
    if runner is None:
        return {
            "response": f"Side question queued: {payload['question']}",
            "queued": True,
        }
    result = runner(payload)
    if isawaitable(result):
        result = await result
    return result


async def call(
    onDone: DoneCallback | None = None,
    context: dict[str, Any] | None = None,
    args: str | None = None,
) -> dict[str, Any]:
    """Ask a quick side question without interrupting the main conversation."""

    question = (args or "").strip()
    if not question:
        result = {"ok": False, "error": "Please provide a question for /btw."}
        await _notify(onDone, result["error"])
        return result

    runtime_context = context or {}
    payload = {"question": question, **buildCacheSafeParams(runtime_context)}
    answer = await _run_side_question(runtime_context, payload)
    if isinstance(answer, dict):
        response = answer.get("response") or answer.get("text") or answer
    else:
        response = str(answer)
    result = {"ok": True, "question": question, "response": response, "raw": answer}
    await _notify(onDone, response)
    return result
