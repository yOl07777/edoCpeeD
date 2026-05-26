from __future__ import annotations

import time
import uuid
from typing import Any

from python_src.entrypoints.sdk.coreSchemas import prompt_response, validate_prompt_request


class AbortError(Exception):
    """Raised when a local SDK operation is cancelled."""


_SESSIONS: dict[str, dict[str, Any]] = {}


def _session(session_id: Any = None) -> dict[str, Any]:
    sid = str(session_id or uuid.uuid4())
    return _SESSIONS.setdefault(
        sid,
        {"id": sid, "provider": "deepseek", "title": "DeepSeek Code session", "tags": [], "messages": [], "createdAt": time.time()},
    )


async def unstable_v2_createSession(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    session = _session(kwargs.get("id"))
    session.update({key: value for key, value in kwargs.items() if key in {"title", "cwd", "model"}})
    return dict(session)


async def unstable_v2_resumeSession(session_id: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    return dict(_session(kwargs.get("session_id") or session_id))


async def getSessionInfo(session_id: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    session = _session(kwargs.get("session_id") or session_id)
    return {key: value for key, value in session.items() if key != "messages"} | {"messageCount": len(session["messages"])}


async def getSessionMessages(session_id: Any = None, *_args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return list(_session(kwargs.get("session_id") or session_id)["messages"])


async def listSessions(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    return [await getSessionInfo(session_id) for session_id in sorted(_SESSIONS)]


async def query(prompt: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    session = _session(kwargs.get("session_id"))
    request = validate_prompt_request({"prompt": kwargs.get("prompt", prompt), "session_id": session["id"], "options": kwargs.get("options", {})})
    text = request["prompt"]
    user = {"role": "user", "content": text}
    assistant = {"role": "assistant", "content": f"DeepSeek local SDK dry-run response for: {text}"}
    session["messages"].extend([user, assistant])
    return {"type": "query_result", **prompt_response(assistant, session_id=session["id"])}


async def unstable_v2_prompt(prompt: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    return await query(prompt, **kwargs)


async def renameSession(session_id: Any = None, title: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    session = _session(kwargs.get("session_id") or session_id)
    session["title"] = str(kwargs.get("title") or title or session.get("title") or "")
    return await getSessionInfo(session["id"])


async def tagSession(session_id: Any = None, tags: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    session = _session(kwargs.get("session_id") or session_id)
    values = kwargs.get("tags", tags if tags is not None else [])
    if isinstance(values, str):
        values = [values]
    session["tags"] = sorted({str(tag) for tag in values or []})
    return await getSessionInfo(session["id"])


async def forkSession(session_id: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    source = _session(kwargs.get("session_id") or session_id)
    fork = _session(kwargs.get("new_session_id"))
    fork.update({key: value for key, value in source.items() if key not in {"id", "createdAt"}})
    fork["forkedFrom"] = source["id"]
    fork["messages"] = list(source.get("messages", []))
    return dict(fork)


async def tool(name: Any = "", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": str(kwargs.get("name") or name or "tool"),
            "description": str(kwargs.get("description") or "DeepSeek SDK tool"),
            "parameters": kwargs.get("parameters") or {"type": "object", "properties": {}},
        },
    }


async def buildMissedTaskNotification(task: Any = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    data = dict(task) if isinstance(task, dict) else {"id": str(task or kwargs.get("task_id", ""))}
    return {"type": "task_notification", "provider": "deepseek", "task": data, "missed": True}


async def connectRemoteControl(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "remote_control", "provider": "deepseek", "connected": False, "dryRun": True, "endpoint": kwargs.get("endpoint", "")}


async def createSdkMcpServer(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "sdk_mcp_server", "provider": "deepseek", "transport": kwargs.get("transport", "stdio"), "dryRun": True}


async def watchScheduledTasks(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "scheduled_tasks_watch", "provider": "deepseek", "tasks": list(kwargs.get("tasks", []) or []), "active": False}


__all__ = [
    "AbortError",
    "buildMissedTaskNotification",
    "connectRemoteControl",
    "createSdkMcpServer",
    "forkSession",
    "getSessionInfo",
    "getSessionMessages",
    "listSessions",
    "query",
    "renameSession",
    "tagSession",
    "tool",
    "unstable_v2_createSession",
    "unstable_v2_prompt",
    "unstable_v2_resumeSession",
    "watchScheduledTasks",
]
