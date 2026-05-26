"""Pure helpers for bridge message routing and control responses."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import re
import uuid as uuidlib
from collections.abc import Callable
from typing import Any


class BoundedUUIDSet:
    def __init__(self, capacity: int) -> None:
        self.capacity = max(1, capacity)
        self.ring: list[str | None] = [None] * self.capacity
        self.set: set[str] = set()
        self.writeIdx = 0

    def add(self, uuid: str) -> None:
        if uuid in self.set:
            return
        evicted = self.ring[self.writeIdx]
        if evicted is not None:
            self.set.discard(evicted)
        self.ring[self.writeIdx] = uuid
        self.set.add(uuid)
        self.writeIdx = (self.writeIdx + 1) % self.capacity

    def has(self, uuid: str) -> bool:
        return uuid in self.set

    def clear(self) -> None:
        self.set.clear()
        self.ring = [None] * self.capacity
        self.writeIdx = 0


def isSDKMessage(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("type"), str)


def isSDKControlResponse(value: Any) -> bool:
    return isinstance(value, dict) and value.get("type") == "control_response" and "response" in value


def isSDKControlRequest(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("type") == "control_request"
        and "request_id" in value
        and isinstance(value.get("request"), dict)
    )


def isEligibleBridgeMessage(m: dict[str, Any]) -> bool:
    msg_type = m.get("type")
    if msg_type in {"user", "assistant"} and m.get("isVirtual"):
        return False
    return msg_type in {"user", "assistant"} or (
        msg_type == "system" and m.get("subtype") == "local_command"
    )


_DISPLAY_TAG_RE = re.compile(r"<(?:ide_opened_file|session-start-hook|[^>\n]+)>.*?</[^>\n]+>|<[^>\n]+/>", re.DOTALL)


def extractTitleText(m: dict[str, Any]) -> str | None:
    if m.get("type") != "user" or m.get("isMeta") or m.get("toolUseResult") or m.get("isCompactSummary"):
        return None
    origin = m.get("origin")
    if isinstance(origin, dict) and origin.get("kind") != "human":
        return None
    message = m.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    raw: str | None = None
    if isinstance(content, str):
        raw = content
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                raw = str(block.get("text", ""))
                break
    if not raw:
        return None
    clean = _DISPLAY_TAG_RE.sub("", raw).strip()
    return clean or None


def _fire(callback: Callable[..., Any] | None, *args: Any) -> None:
    if callback is None:
        return
    result = callback(*args)
    if inspect.isawaitable(result):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(result)
        except RuntimeError:
            asyncio.run(result)


def handleIngressMessage(
    data: str,
    recentPostedUUIDs: BoundedUUIDSet,
    recentInboundUUIDs: BoundedUUIDSet,
    onInboundMessage: Callable[[dict[str, Any]], Any] | None,
    onPermissionResponse: Callable[[dict[str, Any]], Any] | None = None,
    onControlRequest: Callable[[dict[str, Any]], Any] | None = None,
) -> None:
    try:
        parsed = json.loads(data)
    except ValueError:
        return
    if isSDKControlResponse(parsed):
        _fire(onPermissionResponse, parsed)
        return
    if isSDKControlRequest(parsed):
        _fire(onControlRequest, parsed)
        return
    if not isSDKMessage(parsed):
        return
    msg_uuid = parsed.get("uuid") if isinstance(parsed.get("uuid"), str) else None
    if msg_uuid and (recentPostedUUIDs.has(msg_uuid) or recentInboundUUIDs.has(msg_uuid)):
        return
    if parsed.get("type") == "user":
        if msg_uuid:
            recentInboundUUIDs.add(msg_uuid)
        _fire(onInboundMessage, parsed)


OUTBOUND_ONLY_ERROR = (
    "This session is outbound-only. Enable Remote Control locally to allow inbound control."
)


def _success_response(request_id: str, response: dict[str, Any] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"subtype": "success", "request_id": request_id}
    if response is not None:
        body["response"] = response
    return {"type": "control_response", "response": body}


def _error_response(request_id: str, error: str) -> dict[str, Any]:
    return {
        "type": "control_response",
        "response": {"subtype": "error", "request_id": request_id, "error": error},
    }


def handleServerControlRequest(request: dict[str, Any], handlers: dict[str, Any]) -> dict[str, Any] | None:
    transport = handlers.get("transport")
    session_id = handlers.get("sessionId") or handlers.get("session_id")
    req = request.get("request", {}) if isinstance(request, dict) else {}
    subtype = req.get("subtype")
    request_id = str(request.get("request_id", ""))
    if not transport:
        return None
    if handlers.get("outboundOnly") and subtype != "initialize":
        response = _error_response(request_id, OUTBOUND_ONLY_ERROR)
    elif subtype == "initialize":
        response = _success_response(
            request_id,
            {
                "commands": [],
                "output_style": "normal",
                "available_output_styles": ["normal"],
                "models": [],
                "account": {},
                "pid": os.getpid(),
            },
        )
    elif subtype == "set_model":
        _fire(handlers.get("onSetModel"), req.get("model"))
        response = _success_response(request_id)
    elif subtype == "set_max_thinking_tokens":
        _fire(handlers.get("onSetMaxThinkingTokens"), req.get("max_thinking_tokens"))
        response = _success_response(request_id)
    elif subtype == "set_permission_mode":
        verdict = handlers.get("onSetPermissionMode", lambda _mode: {"ok": False, "error": "set_permission_mode is not supported"})(req.get("mode"))
        response = _success_response(request_id) if verdict.get("ok") else _error_response(request_id, str(verdict.get("error")))
    elif subtype == "interrupt":
        _fire(handlers.get("onInterrupt"))
        response = _success_response(request_id)
    else:
        response = _error_response(request_id, f"REPL bridge does not handle control_request subtype: {subtype}")
    event = dict(response)
    if session_id:
        event["session_id"] = session_id
    write_result = transport.write(event) if hasattr(transport, "write") else None
    if inspect.isawaitable(write_result):
        try:
            asyncio.get_running_loop().create_task(write_result)
        except RuntimeError:
            asyncio.run(write_result)
    return event


def makeResultMessage(sessionId: str) -> dict[str, Any]:
    empty_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    return {
        "type": "result",
        "subtype": "success",
        "duration_ms": 0,
        "duration_api_ms": 0,
        "is_error": False,
        "num_turns": 0,
        "result": "",
        "stop_reason": None,
        "total_cost_usd": 0,
        "usage": empty_usage,
        "modelUsage": {},
        "permission_denials": [],
        "session_id": sessionId,
        "uuid": str(uuidlib.uuid4()),
    }
