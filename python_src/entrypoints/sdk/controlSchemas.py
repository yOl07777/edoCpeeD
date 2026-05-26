from __future__ import annotations

from typing import Any


def _schema(name: str, *, kind: str = "object", properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"title": name, "type": kind, "provider": "deepseek"}
    if properties is not None:
        schema["properties"] = properties
    if required:
        schema["required"] = required
    return schema


ControlErrorResponseSchema = _schema(
    "ControlErrorResponseSchema",
    properties={
        "ok": {"type": "boolean", "enum": [False]},
        "error": {"type": "string"},
        "code": {"type": "string"},
    },
    required=["ok", "error"],
)
ControlResponseSchema = _schema(
    "ControlResponseSchema",
    properties={"ok": {"type": "boolean"}, "result": {"type": "object"}, "error": {"type": "string"}},
    required=["ok"],
)
SDKControlInitializeRequestSchema = _schema(
    "SDKControlInitializeRequestSchema",
    properties={
        "type": {"type": "string", "enum": ["initialize"]},
        "cwd": {"type": "string"},
        "model": {"type": "string"},
        "provider": {"type": "string", "enum": ["deepseek"]},
    },
)
SDKControlSetModelRequestSchema = _schema(
    "SDKControlSetModelRequestSchema",
    properties={"type": {"type": "string", "enum": ["set_model"]}, "model": {"type": "string"}},
    required=["model"],
)
SDKControlGetContextUsageResponseSchema = _schema(
    "SDKControlGetContextUsageResponseSchema",
    properties={"ok": {"type": "boolean"}, "tokens": {"type": "integer"}, "messages": {"type": "integer"}},
)
SDKControlRequestSchema = _schema(
    "SDKControlRequestSchema",
    properties={"id": {"type": "string"}, "method": {"type": "string"}, "params": {"type": "object"}},
    required=["method"],
)
SDKControlResponseSchema = _schema(
    "SDKControlResponseSchema",
    properties={"id": {"type": "string"}, "ok": {"type": "boolean"}, "result": {"type": "object"}, "error": {"type": "string"}},
    required=["ok"],
)


_NAMES = """
ControlErrorResponseSchema ControlResponseSchema JSONRPCMessagePlaceholder
SDKControlApplyFlagSettingsRequestSchema SDKControlCancelAsyncMessageRequestSchema
SDKControlCancelAsyncMessageResponseSchema SDKControlCancelRequestSchema
SDKControlElicitationRequestSchema SDKControlElicitationResponseSchema
SDKControlGetContextUsageRequestSchema SDKControlGetContextUsageResponseSchema
SDKControlGetSettingsRequestSchema SDKControlGetSettingsResponseSchema
SDKControlInitializeRequestSchema SDKControlInitializeResponseSchema
SDKControlInterruptRequestSchema SDKControlMcpMessageRequestSchema
SDKControlMcpReconnectRequestSchema SDKControlMcpSetServersRequestSchema
SDKControlMcpSetServersResponseSchema SDKControlMcpStatusRequestSchema
SDKControlMcpStatusResponseSchema SDKControlMcpToggleRequestSchema
SDKControlPermissionRequestSchema SDKControlReloadPluginsRequestSchema
SDKControlReloadPluginsResponseSchema SDKControlRequestInnerSchema
SDKControlRequestSchema SDKControlResponseSchema SDKControlRewindFilesRequestSchema
SDKControlRewindFilesResponseSchema SDKControlSeedReadStateRequestSchema
SDKControlSetMaxThinkingTokensRequestSchema SDKControlSetModelRequestSchema
SDKControlSetPermissionModeRequestSchema SDKControlStopTaskRequestSchema
SDKHookCallbackMatcherSchema SDKHookCallbackRequestSchema SDKKeepAliveMessageSchema
SDKUpdateEnvironmentVariablesMessageSchema StdinMessageSchema StdoutMessageSchema
""".split()

for name in _NAMES:
    globals().setdefault(name, _schema(name))


def control_success(result: dict[str, Any] | None = None, *, request_id: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"ok": True, "provider": "deepseek", "result": result or {}}
    if request_id is not None:
        response["id"] = request_id
    return response


def control_error(error: str, *, code: str = "error", request_id: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"ok": False, "provider": "deepseek", "error": str(error), "code": code}
    if request_id is not None:
        response["id"] = request_id
    return response


def parse_control_request(message: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(message, dict):
        raise TypeError("Control request must be a dict")
    method = message.get("method") or message.get("type")
    if not method:
        raise ValueError("Control request requires 'method' or 'type'")
    params = message.get("params") or {}
    if not isinstance(params, dict):
        raise TypeError("Control request params must be a dict")
    return {"id": message.get("id"), "method": str(method), "params": params}


__all__ = ["control_error", "control_success", "parse_control_request", *_NAMES]
