"""Background memory-consolidation scheduler."""

from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from python_src.bootstrap.state import getIsRemoteMode, getKairosActive, getOriginalCwd, getSessionId
from python_src.memdir.paths import getAutoMemPath, isAutoMemoryEnabled
from python_src.services.autoDream.config import isAutoDreamEnabled
from python_src.services.autoDream.consolidationLock import (
    listSessionsTouchedSince,
    readLastConsolidatedAt,
    rollbackConsolidationLock,
    tryAcquireConsolidationLock,
)
from python_src.services.autoDream.consolidationPrompt import buildConsolidationPrompt
from python_src.tasks.DreamTask.DreamTask import (
    addDreamTurn,
    completeDreamTask,
    failDreamTask,
    isDreamTask,
    registerDreamTask,
)
from python_src.utils.sessionStoragePortable import getProjectDir


SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000
DEFAULTS = {"minHours": 24.0, "minSessions": 5}
_runner: Callable[[dict[str, Any], Callable[[dict[str, Any]], None] | None], Awaitable[dict[str, Any] | None]] | None = None


@dataclass
class AbortController:
    aborted: bool = False
    signal: dict[str, bool] = field(default_factory=lambda: {"aborted": False})

    def abort(self) -> None:
        self.aborted = True
        self.signal["aborted"] = True


def getConfig() -> dict[str, float | int]:
    def number_env(name: str, default: float) -> float:
        try:
            value = float(os.getenv(name, ""))
        except ValueError:
            return default
        return value if value > 0 else default

    return {
        "minHours": number_env("DEEPSEEK_AUTO_DREAM_MIN_HOURS", DEFAULTS["minHours"]),
        "minSessions": int(number_env("DEEPSEEK_AUTO_DREAM_MIN_SESSIONS", DEFAULTS["minSessions"])),
    }


async def isGateOpen() -> bool:
    if getKairosActive() or getIsRemoteMode():
        return False
    if not isAutoMemoryEnabled():
        return False
    return await isAutoDreamEnabled()


def isForced() -> bool:
    return str(os.getenv("DEEPSEEK_AUTO_DREAM_FORCE") or "").strip().lower() in {"1", "true", "yes", "on"}


def _context_tool_context(context: dict[str, Any]) -> dict[str, Any]:
    return context.get("toolUseContext") or context.get("tool_use_context") or context


def _get_app_state(context: dict[str, Any]) -> dict[str, Any]:
    tool_context = _context_tool_context(context)
    getter = tool_context.get("getAppState")
    if callable(getter):
        return getter()
    return tool_context.get("appState") or context.get("appState") or {"tasks": {}}


def _get_set_app_state(context: dict[str, Any]) -> Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None]:
    tool_context = _context_tool_context(context)
    setter = tool_context.get("setAppStateForTasks") or tool_context.get("setAppState")
    if callable(setter):
        return setter

    app_state = _get_app_state(context)

    def set_app_state(updater: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        app_state.clear()
        app_state.update(updater(dict(app_state)))

    return set_app_state


def makeDreamProgressWatcher(
    taskId: str,
    setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None],
) -> Callable[[dict[str, Any]], None]:
    def watcher(msg: dict[str, Any]) -> None:
        if msg.get("type") != "assistant":
            return
        content = (msg.get("message") or {}).get("content") or msg.get("content") or []
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        text = ""
        tool_use_count = 0
        touched: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text += str(block.get("text") or "")
            elif block.get("type") in {"tool_use", "tool_call"}:
                tool_use_count += 1
                name = block.get("name") or (block.get("function") or {}).get("name")
                if name in {"Edit", "Write", "FileEdit", "FileWrite"}:
                    input_value = block.get("input") or block.get("arguments") or {}
                    if isinstance(input_value, dict) and isinstance(input_value.get("file_path"), str):
                        touched.append(input_value["file_path"])
        addDreamTurn(taskId, {"text": text.strip(), "toolUseCount": tool_use_count}, touched, setAppState)

    return watcher


async def _default_fork_runner(
    *,
    prompt: str,
    taskId: str,
    setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None],
    context: dict[str, Any],
    abortController: AbortController,
) -> dict[str, Any]:
    """Dry, deterministic runner used until a real forked-agent bridge exists."""

    callback = context.get("runForkedAgent") or _context_tool_context(context).get("runForkedAgent")
    if callable(callback):
        result = callback(
            {
                "prompt": prompt,
                "querySource": "auto_dream",
                "forkLabel": "auto_dream",
                "onMessage": makeDreamProgressWatcher(taskId, setAppState),
                "abortController": abortController,
            }
        )
        if hasattr(result, "__await__"):
            return await result
        return result
    return {"status": "planned", "prompt": prompt, "totalUsage": {"output_tokens": 0}}


def initAutoDream(*_: Any, **__: Any) -> None:
    last_session_scan_at = 0.0

    async def run_auto_dream(
        context: dict[str, Any],
        appendSystemMessage: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any] | None:
        nonlocal last_session_scan_at
        cfg = getConfig()
        force = isForced()
        if not force and not await isGateOpen():
            return {"status": "skipped", "reason": "gate_closed"}

        last_at = await readLastConsolidatedAt()
        hours_since = (time.time() * 1000 - last_at) / 3_600_000
        if not force and hours_since < float(cfg["minHours"]):
            return {"status": "skipped", "reason": "time_gate", "hoursSince": hours_since}

        since_scan_ms = time.time() * 1000 - last_session_scan_at
        if not force and since_scan_ms < SESSION_SCAN_INTERVAL_MS:
            return {"status": "skipped", "reason": "scan_throttle"}
        last_session_scan_at = time.time() * 1000

        session_ids = await listSessionsTouchedSince(last_at)
        current_session = getSessionId()
        session_ids = [item for item in session_ids if item != current_session]
        if not force and len(session_ids) < int(cfg["minSessions"]):
            return {
                "status": "skipped",
                "reason": "session_gate",
                "sessionsSince": len(session_ids),
                "minSessions": int(cfg["minSessions"]),
            }

        prior_mtime = last_at if force else await tryAcquireConsolidationLock()
        if prior_mtime is None:
            return {"status": "skipped", "reason": "lock_held"}

        set_app_state = _get_set_app_state(context)
        abort_controller = AbortController()
        task_id = registerDreamTask(
            set_app_state,
            {
                "sessionsReviewing": len(session_ids),
                "priorMtime": prior_mtime,
                "abortController": abort_controller,
            },
        )

        memory_root = getAutoMemPath()
        transcript_dir = await getProjectDir(getOriginalCwd())
        extra = (
            "\n\n**Tool constraints for this run:** Use read-only shell commands for exploration. "
            "Use file edit/write tools for memory updates.\n\n"
            f"Sessions since last consolidation ({len(session_ids)}):\n"
            + "\n".join(f"- {item}" for item in session_ids)
        )
        prompt = await buildConsolidationPrompt(memory_root, transcript_dir, extra)

        try:
            result = await _default_fork_runner(
                prompt=prompt,
                taskId=task_id,
                setAppState=set_app_state,
                context=context,
                abortController=abort_controller,
            )
            completeDreamTask(task_id, set_app_state)
            dream_state = (_get_app_state(context).get("tasks") or {}).get(task_id)
            if appendSystemMessage and isDreamTask(dream_state) and dream_state.get("filesTouched"):
                appendSystemMessage(
                    {
                        "type": "system",
                        "level": "info",
                        "message": f"Improved memory files: {', '.join(dream_state['filesTouched'])}",
                    }
                )
            return {
                "status": "completed",
                "taskId": task_id,
                "sessionsReviewed": len(session_ids),
                "prompt": prompt,
                "result": result,
            }
        except Exception as exc:
            if abort_controller.aborted:
                return {"status": "aborted", "taskId": task_id}
            failDreamTask(task_id, set_app_state)
            await rollbackConsolidationLock(float(prior_mtime))
            return {"status": "failed", "taskId": task_id, "error": str(exc)}

    global _runner
    _runner = run_auto_dream


async def executeAutoDream(
    context: dict[str, Any] | None = None,
    appendSystemMessage: Callable[[dict[str, Any]], None] | None = None,
    *_: Any,
    **__: Any,
) -> dict[str, Any] | None:
    if _runner is None:
        initAutoDream()
    assert _runner is not None
    return await _runner(context or {}, appendSystemMessage)


__all__ = [
    "AbortController",
    "SESSION_SCAN_INTERVAL_MS",
    "executeAutoDream",
    "getConfig",
    "initAutoDream",
    "isForced",
    "isGateOpen",
    "makeDreamProgressWatcher",
]
