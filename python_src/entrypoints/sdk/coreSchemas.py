from __future__ import annotations

from typing import Any


def _schema(name: str, *, kind: str = "object", properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"title": name, "type": kind, "provider": "deepseek"}
    if properties is not None:
        schema["properties"] = properties
    if required:
        schema["required"] = required
    return schema


RoleSchema = {"type": "string", "enum": ["system", "user", "assistant", "tool"]}
ContentBlockSchema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["text", "image_url"]},
        "text": {"type": "string"},
        "image_url": {"type": "object", "properties": {"url": {"type": "string"}}},
    },
}
ToolCallSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "type": {"type": "string", "enum": ["function"]},
        "function": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "arguments": {"type": "string"},
            },
            "required": ["name", "arguments"],
        },
    },
    "required": ["id", "type", "function"],
}

APIUserMessagePlaceholder = _schema(
    "APIUserMessagePlaceholder",
    properties={
        "role": RoleSchema,
        "content": {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": ContentBlockSchema},
            ]
        },
    },
    required=["role", "content"],
)
APIAssistantMessagePlaceholder = _schema(
    "APIAssistantMessagePlaceholder",
    properties={
        "role": {"type": "string", "enum": ["assistant"]},
        "content": {"type": ["string", "null"]},
        "reasoning_content": {"type": "string"},
        "tool_calls": {"type": "array", "items": ToolCallSchema},
    },
    required=["role"],
)
ModelUsageSchema = _schema(
    "ModelUsageSchema",
    properties={
        "prompt_tokens": {"type": "integer"},
        "completion_tokens": {"type": "integer"},
        "total_tokens": {"type": "integer"},
    },
)
PromptRequestOptionSchema = _schema(
    "PromptRequestOptionSchema",
    properties={
        "model": {"type": "string"},
        "stream": {"type": "boolean"},
        "max_tokens": {"type": "integer"},
        "temperature": {"type": "number"},
        "tools": {"type": "array"},
    },
)
PromptRequestSchema = _schema(
    "PromptRequestSchema",
    properties={
        "prompt": {"type": "string"},
        "messages": {"type": "array", "items": {"type": "object"}},
        "options": PromptRequestOptionSchema,
        "cwd": {"type": "string"},
        "session_id": {"type": "string"},
    },
)
PromptResponseSchema = _schema(
    "PromptResponseSchema",
    properties={
        "type": {"type": "string", "enum": ["prompt_response"]},
        "provider": {"type": "string", "enum": ["deepseek"]},
        "session_id": {"type": "string"},
        "message": APIAssistantMessagePlaceholder,
        "usage": ModelUsageSchema,
    },
    required=["type", "provider", "message"],
)
SDKMessageSchema = _schema(
    "SDKMessageSchema",
    properties={
        "type": {"type": "string"},
        "provider": {"type": "string", "enum": ["deepseek"]},
        "session_id": {"type": "string"},
        "message": {"type": "object"},
        "usage": ModelUsageSchema,
    },
)
SDKResultSuccessSchema = _schema(
    "SDKResultSuccessSchema",
    properties={"type": {"type": "string", "enum": ["result"]}, "subtype": {"type": "string", "enum": ["success"]}, "result": {"type": "object"}},
)
SDKResultErrorSchema = _schema(
    "SDKResultErrorSchema",
    properties={"type": {"type": "string", "enum": ["result"]}, "subtype": {"type": "string", "enum": ["error"]}, "error": {"type": "string"}},
)
OutputFormatTypeSchema = {"type": "string", "enum": ["text", "json", "stream-json"]}
OutputFormatSchema = _schema(
    "OutputFormatSchema",
    properties={"type": OutputFormatTypeSchema, "schema": {"type": "object"}},
)


EXIT_REASONS = ["success", "error", "cancelled", "interrupted"]
HOOK_EVENTS = ["PreToolUse", "PostToolUse", "Notification", "UserPromptSubmit", "SessionStart", "SessionEnd", "Stop"]
CONFIG_CHANGE_SOURCES = ["user", "project", "environment", "default"]
INSTRUCTIONS_LOAD_REASONS = ["startup", "resume", "manual"]
INSTRUCTIONS_MEMORY_TYPES = ["project", "user", "team"]

_SCHEMA_NAMES = """
APIAssistantMessagePlaceholder APIUserMessagePlaceholder AccountInfoSchema AgentDefinitionSchema
AgentInfoSchema AgentMcpServerSpecSchema ApiKeySourceSchema AsyncHookJSONOutputSchema
BaseHookInputSchema BaseOutputFormatSchema ConfigChangeHookInputSchema ConfigScopeSchema
CwdChangedHookInputSchema CwdChangedHookSpecificOutputSchema ElicitationHookInputSchema
ElicitationHookSpecificOutputSchema ElicitationResultHookInputSchema
ElicitationResultHookSpecificOutputSchema ExitReasonSchema FastModeStateSchema
FileChangedHookInputSchema FileChangedHookSpecificOutputSchema HookEventSchema HookInputSchema
HookJSONOutputSchema InstructionsLoadedHookInputSchema JsonSchemaOutputFormatSchema
McpClaudeAIProxyServerConfigSchema McpHttpServerConfigSchema McpSSEServerConfigSchema
McpSdkServerConfigSchema McpServerConfigForProcessTransportSchema McpServerStatusConfigSchema
McpServerStatusSchema McpSetServersResultSchema McpStdioServerConfigSchema ModelInfoSchema
ModelUsageSchema NonNullableUsagePlaceholder NotificationHookInputSchema
NotificationHookSpecificOutputSchema OutputFormatSchema OutputFormatTypeSchema
PermissionBehaviorSchema PermissionDecisionClassificationSchema PermissionDeniedHookInputSchema
PermissionDeniedHookSpecificOutputSchema PermissionModeSchema PermissionRequestHookInputSchema
PermissionRequestHookSpecificOutputSchema PermissionResultSchema PermissionRuleValueSchema
PermissionUpdateDestinationSchema PermissionUpdateSchema PostCompactHookInputSchema
PostToolUseFailureHookInputSchema PostToolUseFailureHookSpecificOutputSchema
PostToolUseHookInputSchema PostToolUseHookSpecificOutputSchema PreCompactHookInputSchema
PreToolUseHookInputSchema PreToolUseHookSpecificOutputSchema PromptRequestOptionSchema
PromptRequestSchema PromptResponseSchema RawMessageStreamEventPlaceholder RewindFilesResultSchema
SDKAPIRetryMessageSchema SDKAssistantMessageErrorSchema SDKAssistantMessageSchema
SDKAuthStatusMessageSchema SDKCompactBoundaryMessageSchema SDKElicitationCompleteMessageSchema
SDKFilesPersistedEventSchema SDKHookProgressMessageSchema SDKHookResponseMessageSchema
SDKHookStartedMessageSchema SDKLocalCommandOutputMessageSchema SDKMessageSchema
SDKPartialAssistantMessageSchema SDKPermissionDenialSchema SDKPostTurnSummaryMessageSchema
SDKPromptSuggestionMessageSchema SDKRateLimitEventSchema SDKRateLimitInfoSchema
SDKResultErrorSchema SDKResultMessageSchema SDKResultSuccessSchema SDKSessionInfoSchema
SDKSessionStateChangedMessageSchema SDKStatusMessageSchema SDKStatusSchema
SDKStreamlinedTextMessageSchema SDKStreamlinedToolUseSummaryMessageSchema SDKSystemMessageSchema
SDKTaskNotificationMessageSchema SDKTaskProgressMessageSchema SDKTaskStartedMessageSchema
SDKToolProgressMessageSchema SDKToolUseSummaryMessageSchema SDKUserMessageReplaySchema
SDKUserMessageSchema SdkBetaSchema SdkPluginConfigSchema SessionEndHookInputSchema
SessionStartHookInputSchema SessionStartHookSpecificOutputSchema SettingSourceSchema
SetupHookInputSchema SetupHookSpecificOutputSchema SlashCommandSchema StopFailureHookInputSchema
StopHookInputSchema SubagentStartHookInputSchema SubagentStartHookSpecificOutputSchema
SubagentStopHookInputSchema SyncHookJSONOutputSchema TaskCompletedHookInputSchema
TaskCreatedHookInputSchema TeammateIdleHookInputSchema ThinkingAdaptiveSchema
ThinkingConfigSchema ThinkingDisabledSchema ThinkingEnabledSchema UUIDPlaceholder
UserPromptSubmitHookInputSchema UserPromptSubmitHookSpecificOutputSchema WorktreeCreateHookInputSchema
WorktreeCreateHookSpecificOutputSchema WorktreeRemoveHookInputSchema
""".split()

for name in _SCHEMA_NAMES:
    globals().setdefault(name, _schema(name))


def sdk_message(message_type: str, **payload: Any) -> dict[str, Any]:
    return {"type": message_type, "provider": "deepseek", **payload}


def prompt_response(message: dict[str, Any], *, session_id: str | None = None, usage: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    if usage:
        payload["usage"] = usage
    return sdk_message("prompt_response", **payload)


def validate_prompt_request(request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise TypeError("Prompt request must be a dict")
    prompt = request.get("prompt")
    messages = request.get("messages")
    if prompt is None and messages is None:
        raise ValueError("Prompt request requires either 'prompt' or 'messages'")
    if messages is not None and not isinstance(messages, list):
        raise TypeError("'messages' must be a list")
    options = request.get("options") or {}
    if options and not isinstance(options, dict):
        raise TypeError("'options' must be a dict")
    return {
        "prompt": "" if prompt is None else str(prompt),
        "messages": messages or [],
        "options": options,
        "cwd": request.get("cwd"),
        "session_id": request.get("session_id"),
    }


def normalize_output_format(value: str | dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {"type": "text"}
    if isinstance(value, str):
        kind = value.lower().strip()
        if kind not in {"text", "json", "stream-json"}:
            raise ValueError(f"Unsupported output format: {value}")
        return {"type": kind}
    kind = str(value.get("type") or "text").lower()
    if kind not in {"text", "json", "stream-json"}:
        raise ValueError(f"Unsupported output format: {kind}")
    return {"type": kind, **{key: item for key, item in value.items() if key != "type"}}


__all__ = [
    "CONFIG_CHANGE_SOURCES",
    "EXIT_REASONS",
    "HOOK_EVENTS",
    "INSTRUCTIONS_LOAD_REASONS",
    "INSTRUCTIONS_MEMORY_TYPES",
    "normalize_output_format",
    "prompt_response",
    "sdk_message",
    "validate_prompt_request",
    *_SCHEMA_NAMES,
]
