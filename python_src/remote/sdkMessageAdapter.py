"""SDK-to-local message adapter for remote sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _system_message(
    content: str,
    *,
    uuid: str | None = None,
    level: str = "info",
    subtype: str = "informational",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "type": "system",
        "subtype": subtype,
        "content": content,
        "level": level,
        "uuid": uuid,
        "timestamp": _now(),
        **extra,
    }


def _create_user_message(msg: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "user",
        "message": {"role": "user", "content": msg.get("content")},
        "uuid": msg.get("uuid"),
        "timestamp": msg.get("timestamp") or _now(),
        "toolUseResult": msg.get("tool_use_result"),
    }


def _is_tool_result_content(content: Any) -> bool:
    return isinstance(content, list) and any(
        isinstance(block, dict) and block.get("type") == "tool_result" for block in content
    )


def convertSDKMessage(msg: dict[str, Any], opts: dict[str, Any] | None = None) -> dict[str, Any]:
    opts = opts or {}
    msg_type = msg.get("type")

    if msg_type == "assistant":
        return {
            "type": "message",
            "message": {
                "type": "assistant",
                "message": msg.get("message"),
                "uuid": msg.get("uuid"),
                "requestId": None,
                "timestamp": _now(),
                "error": msg.get("error"),
            },
        }

    if msg_type == "user":
        message = msg.get("message") or {}
        content = message.get("content")
        is_tool_result = _is_tool_result_content(content)
        if opts.get("convertToolResults") and is_tool_result:
            return {"type": "message", "message": _create_user_message({**msg, "content": content})}
        if opts.get("convertUserTextMessages") and not is_tool_result and isinstance(content, (str, list)):
            return {"type": "message", "message": _create_user_message({**msg, "content": content})}
        return {"type": "ignored"}

    if msg_type == "stream_event":
        return {"type": "stream_event", "event": {"type": "stream_event", "event": msg.get("event")}}

    if msg_type == "result":
        if msg.get("subtype") != "success":
            errors = msg.get("errors") or []
            content = ", ".join(str(e) for e in errors) if errors else "Unknown error"
            return {
                "type": "message",
                "message": _system_message(content, uuid=msg.get("uuid"), level="warning"),
            }
        return {"type": "ignored"}

    if msg_type == "system":
        subtype = msg.get("subtype")
        if subtype == "init":
            return {
                "type": "message",
                "message": _system_message(
                    f"Remote session initialized (model: {msg.get('model')})",
                    uuid=msg.get("uuid"),
                ),
            }
        if subtype == "status":
            status = msg.get("status")
            if not status:
                return {"type": "ignored"}
            content = "Compacting conversation..." if status == "compacting" else f"Status: {status}"
            return {"type": "message", "message": _system_message(content, uuid=msg.get("uuid"))}
        if subtype == "compact_boundary":
            return {
                "type": "message",
                "message": _system_message(
                    "Conversation compacted",
                    uuid=msg.get("uuid"),
                    subtype="compact_boundary",
                    compactMetadata=msg.get("compact_metadata"),
                ),
            }
        return {"type": "ignored"}

    if msg_type == "tool_progress":
        content = f"Tool {msg.get('tool_name')} running for {msg.get('elapsed_time_seconds')}s..."
        return {
            "type": "message",
            "message": _system_message(content, uuid=msg.get("uuid"), toolUseID=msg.get("tool_use_id")),
        }

    return {"type": "ignored"}


def isSessionEndMessage(msg: dict[str, Any]) -> bool:
    return msg.get("type") == "result"


def isSuccessResult(msg: dict[str, Any]) -> bool:
    return msg.get("subtype") == "success"


def getResultText(msg: dict[str, Any]) -> str | None:
    if isSuccessResult(msg):
        result = msg.get("result")
        return str(result) if result is not None else None
    return None


__all__ = ["convertSDKMessage", "getResultText", "isSessionEndMessage", "isSuccessResult"]
