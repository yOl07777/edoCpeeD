"""Local teammate mailbox utilities."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_MAILBOX: list[dict[str, Any]] = []


def _schema(message_type: str) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {"type": {"const": message_type}, "id": {"type": "string"}, "created_at": {"type": "string"}},
        "required": ["type"],
        "additionalProperties": True,
    }


ModeSetRequestMessageSchema = _schema("mode_set_request")
PlanApprovalRequestMessageSchema = _schema("plan_approval_request")
PlanApprovalResponseMessageSchema = _schema("plan_approval_response")
ShutdownApprovedMessageSchema = _schema("shutdown_approved")
ShutdownRejectedMessageSchema = _schema("shutdown_rejected")
ShutdownRequestMessageSchema = _schema("shutdown_request")


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _message(message_type: str, **fields: Any) -> dict[str, Any]:
    result = {
        "type": message_type,
        "id": fields.pop("id", None) or uuid.uuid4().hex,
        "created_at": fields.pop("created_at", None) or datetime.now(timezone.utc).isoformat(),
        "read": bool(fields.pop("read", False)),
    }
    result.update(fields)
    return result


def _path(value: str | Path | None = None) -> Path:
    if value:
        return Path(value).expanduser()
    return Path(os.getenv("DEEPCODE_TEAMMATE_MAILBOX", ".deepseek_teammate_mailbox.jsonl")).expanduser()


def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    messages: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            messages.append(_message("raw", text=line))
    return messages


def _save(path: Path, messages: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in messages), encoding="utf-8")


async def getInboxPath(*args: Any, **kwargs: Any) -> str:
    return str(_path(args[0] if args else kwargs.get("path")))


async def writeToMailbox(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    path = _path(data.pop("path", None))
    message = data.get("message") if isinstance(data.get("message"), dict) else data
    message = dict(message)
    message.setdefault("type", "message")
    message.setdefault("id", uuid.uuid4().hex)
    message.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    message.setdefault("read", False)
    messages = _load(path)
    messages.append(message)
    _save(path, messages)
    _MAILBOX.append(message)
    return message


async def readMailbox(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    path_value = args[0] if args else kwargs.get("path")
    if path_value is None and _MAILBOX:
        return [dict(item) for item in _MAILBOX]
    return _load(_path(path_value))


async def clearMailbox(*args: Any, **kwargs: Any) -> dict[str, int]:
    path = _path(args[0] if args else kwargs.get("path"))
    messages = _load(path)
    count = len(messages) if messages else len(_MAILBOX)
    _MAILBOX.clear()
    if path.exists():
        path.unlink()
    return {"cleared": count}


async def readUnreadMessages(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return [message for message in await readMailbox(*args, **kwargs) if not message.get("read", False)]


async def markMessageAsReadByIndex(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    path = _path(kwargs.get("path"))
    index = int(args[0] if args else kwargs.get("index", 0))
    messages = _load(path)
    if index < 0 or index >= len(messages):
        return None
    messages[index]["read"] = True
    _save(path, messages)
    return messages[index]


async def markMessagesAsRead(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    path = _path(args[0] if args else kwargs.get("path"))
    messages = _load(path)
    for message in messages:
        message["read"] = True
    _save(path, messages)
    return messages


async def markMessagesAsReadByPredicate(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    predicate = args[0] if args and callable(args[0]) else kwargs.get("predicate")
    path = _path(kwargs.get("path"))
    if not callable(predicate):
        predicate = lambda _message: True
    messages = _load(path)
    marked: list[dict[str, Any]] = []
    for message in messages:
        if predicate(message):
            message["read"] = True
            marked.append(message)
    _save(path, messages)
    return marked


async def createIdleNotification(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("idle_notification", teammate=data.get("teammate"), summary=data.get("summary", ""))


async def createModeSetRequestMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("mode_set_request", mode=data.get("mode"), requester=data.get("requester"))


async def createPermissionRequestMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("permission_request", tool=data.get("tool"), input=data.get("input", {}), requester=data.get("requester"))


async def createPermissionResponseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("permission_response", request_id=data.get("request_id") or data.get("requestId"), approved=bool(data.get("approved", False)), reason=data.get("reason", ""))


async def createSandboxPermissionRequestMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("sandbox_permission_request", command=data.get("command", ""), cwd=data.get("cwd"))


async def createSandboxPermissionResponseMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("sandbox_permission_response", request_id=data.get("request_id") or data.get("requestId"), approved=bool(data.get("approved", False)))


async def createShutdownRequestMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("shutdown_request", reason=data.get("reason", ""))


async def createShutdownApprovedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("shutdown_approved", request_id=data.get("request_id") or data.get("requestId"), reason=data.get("reason", ""))


async def createShutdownRejectedMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return _message("shutdown_rejected", request_id=data.get("request_id") or data.get("requestId"), reason=data.get("reason", ""))


async def sendShutdownRequestToMailbox(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    message = await createShutdownRequestMessage(reason=data.get("reason", ""))
    return await writeToMailbox(message=message, path=data.get("path"))


def _is_type(value: Any, message_type: str) -> bool:
    return isinstance(value, dict) and value.get("type") == message_type


async def isIdleNotification(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "idle_notification")


async def isModeSetRequest(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "mode_set_request")


async def isPermissionRequest(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "permission_request")


async def isPermissionResponse(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "permission_response")


async def isSandboxPermissionRequest(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "sandbox_permission_request")


async def isSandboxPermissionResponse(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "sandbox_permission_response")


async def isShutdownRequest(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "shutdown_request")


async def isShutdownApproved(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "shutdown_approved")


async def isShutdownRejected(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "shutdown_rejected")


async def isPlanApprovalRequest(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "plan_approval_request")


async def isPlanApprovalResponse(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "plan_approval_response")


async def isTaskAssignment(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "task_assignment")


async def isTeamPermissionUpdate(*args: Any, **kwargs: Any) -> bool:
    return _is_type(args[0] if args else kwargs, "team_permission_update")


async def isStructuredProtocolMessage(*args: Any, **kwargs: Any) -> bool:
    value = args[0] if args else kwargs
    return isinstance(value, dict) and isinstance(value.get("type"), str) and isinstance(value.get("id"), str)


async def formatTeammateMessages(*args: Any, **kwargs: Any) -> str:
    messages = list(args[0] if args else kwargs.get("messages", []) or [])
    lines = []
    for message in messages:
        sender = message.get("from") or message.get("sender") or message.get("teammate") or "teammate"
        text = message.get("text") or message.get("summary") or message.get("reason") or message.get("type", "")
        lines.append(f"{sender}: {text}")
    return "\n".join(lines)


async def getLastPeerDmSummary(*args: Any, **kwargs: Any) -> str | None:
    if args:
        messages = list(args[0])
    elif kwargs.get("messages"):
        messages = list(kwargs["messages"])
    else:
        messages = await readMailbox(path=kwargs.get("path"))
    for message in reversed(messages):
        if message.get("type") in {"dm", "message", "idle_notification"}:
            return str(message.get("text") or message.get("summary") or message.get("content") or "")
    return None


__all__ = [
    "ModeSetRequestMessageSchema",
    "PlanApprovalRequestMessageSchema",
    "PlanApprovalResponseMessageSchema",
    "ShutdownApprovedMessageSchema",
    "ShutdownRejectedMessageSchema",
    "ShutdownRequestMessageSchema",
    "clearMailbox",
    "createIdleNotification",
    "createModeSetRequestMessage",
    "createPermissionRequestMessage",
    "createPermissionResponseMessage",
    "createSandboxPermissionRequestMessage",
    "createSandboxPermissionResponseMessage",
    "createShutdownApprovedMessage",
    "createShutdownRejectedMessage",
    "createShutdownRequestMessage",
    "formatTeammateMessages",
    "getInboxPath",
    "getLastPeerDmSummary",
    "isIdleNotification",
    "isModeSetRequest",
    "isPermissionRequest",
    "isPermissionResponse",
    "isPlanApprovalRequest",
    "isPlanApprovalResponse",
    "isSandboxPermissionRequest",
    "isSandboxPermissionResponse",
    "isShutdownApproved",
    "isShutdownRejected",
    "isShutdownRequest",
    "isStructuredProtocolMessage",
    "isTaskAssignment",
    "isTeamPermissionUpdate",
    "markMessageAsReadByIndex",
    "markMessagesAsRead",
    "markMessagesAsReadByPredicate",
    "readMailbox",
    "readUnreadMessages",
    "sendShutdownRequestToMailbox",
    "writeToMailbox",
]
