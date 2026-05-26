"""Headless CLI helpers for the Python DeepSeek migration."""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterable, Callable
from uuid import uuid4

from deepseek_code.core.code_processor import CodeProcessor


def _to_blocks(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [{"type": "text", "text": value}]
    return [value]


def joinPromptValues(values: list[Any]) -> Any:
    if len(values) == 1:
        return values[0]
    if all(isinstance(value, str) for value in values):
        return "\n".join(values)
    blocks: list[Any] = []
    for value in values:
        blocks.extend(_to_blocks(value))
    return blocks


def canBatchWith(head: dict[str, Any], next: dict[str, Any] | None = None) -> bool:
    return bool(
        next is not None
        and next.get("mode") == "prompt"
        and next.get("workload") == head.get("workload")
        and next.get("isMeta") == head.get("isMeta")
    )


def removeInterruptedMessage(messages: list[dict[str, Any]], interruptedUserMessage: dict[str, Any]) -> None:
    target_uuid = interruptedUserMessage.get("uuid")
    for idx, message in enumerate(list(messages)):
        if message.get("uuid") == target_uuid:
            del messages[idx : idx + 2]
            return


def createCanUseToolWithPermissionPrompt(permissionPromptTool: Any) -> Callable[..., Any]:
    async def can_use_tool(
        tool: Any,
        input: dict[str, Any] | None = None,
        toolUseContext: Any = None,
        assistantMessage: Any = None,
        toolUseId: str | None = None,
        forceDecision: Any = None,
    ) -> Any:
        if forceDecision is not None:
            return forceDecision
        if callable(permissionPromptTool):
            return await _maybe_await(permissionPromptTool(tool, input or {}, toolUseContext, assistantMessage, toolUseId))
        call = getattr(permissionPromptTool, "call", None) or getattr(permissionPromptTool, "handler", None)
        if callable(call):
            return await _maybe_await(call({"tool": getattr(tool, "name", None) or (tool.get("name") if isinstance(tool, dict) else str(tool)), "input": input or {}, "toolUseID": toolUseId}))
        return {"behavior": "allow", "updatedInput": input or {}}

    return can_use_tool


def getCanUseToolFn(
    permissionPromptToolName: str | None = None,
    structuredIO: Any = None,
    getMcpTools: Callable[[], list[Any]] | None = None,
    onPermissionPrompt: Callable[..., Any] | None = None,
) -> Callable[..., Any]:
    if not permissionPromptToolName:
        async def default_can_use_tool(
            tool: Any,
            input: dict[str, Any] | None = None,
            toolUseContext: Any = None,
            assistantMessage: Any = None,
            toolUseId: str | None = None,
            forceDecision: Any = None,
        ) -> Any:
            if forceDecision is not None:
                return forceDecision
            if onPermissionPrompt:
                return await _maybe_await(onPermissionPrompt(tool, input or {}, toolUseContext, assistantMessage, toolUseId))
            return {"behavior": "allow", "updatedInput": input or {}}

        return default_can_use_tool

    resolved: Callable[..., Any] | None = None

    async def with_prompt(tool: Any, input: dict[str, Any] | None = None, toolUseContext: Any = None, assistantMessage: Any = None, toolUseId: str | None = None, forceDecision: Any = None) -> Any:
        nonlocal resolved
        if forceDecision is not None:
            return forceDecision
        if resolved is None:
            tools = getMcpTools() if getMcpTools else []
            prompt_tool = next((t for t in tools if (getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)) == permissionPromptToolName), None)
            if prompt_tool is None:
                raise ValueError(f"MCP tool {permissionPromptToolName} not found")
            resolved = createCanUseToolWithPermissionPrompt(prompt_tool)
        return await resolved(tool, input or {}, toolUseContext, assistantMessage, toolUseId, forceDecision)

    return with_prompt


async def handleOrphanedPermissionResponse(
    payload: dict[str, Any] | None = None,
    *,
    message: dict[str, Any] | None = None,
    setAppState: Callable[[Any], Any] | None = None,
    onEnqueued: Callable[[], Any] | None = None,
    handledToolUseIds: set[str] | None = None,
) -> bool:
    msg = message or (payload or {}).get("message") or payload or {}
    handled = handledToolUseIds if handledToolUseIds is not None else set()
    response = msg.get("response", {})
    result = response.get("response") if isinstance(response, dict) else None
    tool_use_id = result.get("toolUseID") if isinstance(result, dict) else None
    if not isinstance(tool_use_id, str) or tool_use_id in handled:
        return False
    handled.add(tool_use_id)
    if onEnqueued:
        onEnqueued()
    if setAppState:
        setAppState(lambda state: state)
    return True


async def reconcileMcpServers(
    desiredConfigs: dict[str, dict[str, Any]],
    currentState: dict[str, Any] | None = None,
    setAppState: Callable[[Any], Any] | None = None,
) -> dict[str, Any]:
    state = currentState or {"configs": {}, "clients": [], "tools": []}
    current = set((state.get("configs") or {}).keys())
    desired = set(desiredConfigs.keys())
    removed = sorted(current - desired)
    added = sorted(desired - current)
    configs = {name: dict(config) for name, config in desiredConfigs.items()}
    tools = [tool for tool in state.get("tools", []) if not any(str(getattr(tool, "name", tool.get("name", "")) if isinstance(tool, dict) else tool).startswith(f"mcp__{name}__") for name in removed)]
    new_state = {"configs": configs, "clients": [c for c in state.get("clients", []) if getattr(c, "name", None) not in removed], "tools": tools}
    if setAppState:
        setAppState(lambda previous: {**previous, "mcp": new_state} if isinstance(previous, dict) else previous)
    return {"response": {"added": added, "removed": removed, "errors": {}}, "newState": new_state}


async def handleMcpSetServers(
    servers: dict[str, dict[str, Any]],
    sdkState: dict[str, Any] | None = None,
    dynamicState: dict[str, Any] | None = None,
    setAppState: Callable[[Any], Any] | None = None,
) -> dict[str, Any]:
    sdk_state = sdkState or {"configs": {}, "clients": [], "tools": []}
    sdk_servers = {name: cfg for name, cfg in servers.items() if cfg.get("type") == "sdk"}
    process_servers = {name: cfg for name, cfg in servers.items() if cfg.get("type") != "sdk"}
    current_sdk = set((sdk_state.get("configs") or {}).keys())
    desired_sdk = set(sdk_servers.keys())
    sdk_added = sorted(desired_sdk - current_sdk)
    sdk_removed = sorted(current_sdk - desired_sdk)
    process_result = await reconcileMcpServers(process_servers, dynamicState, setAppState)
    return {
        "response": {
            "added": sdk_added + process_result["response"]["added"],
            "removed": sdk_removed + process_result["response"]["removed"],
            "errors": process_result["response"]["errors"],
        },
        "newSdkState": {"configs": sdk_servers, "clients": sdk_state.get("clients", []), "tools": sdk_state.get("tools", [])},
        "newDynamicState": process_result["newState"],
        "sdkServersChanged": bool(sdk_added or sdk_removed),
    }


async def runHeadless(
    inputPrompt: str | AsyncIterable[str],
    getAppState: Callable[[], Any] | None = None,
    setAppState: Callable[[Any], Any] | None = None,
    commands: list[Any] | None = None,
    tools: list[Any] | None = None,
    sdkMcpConfigs: dict[str, Any] | None = None,
    agents: list[Any] | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    opts = options or {}
    if isinstance(inputPrompt, str):
        prompt = inputPrompt
    else:
        parts: list[str] = []
        async for chunk in inputPrompt:
            parts.append(str(chunk))
        prompt = "".join(parts)
    if opts.get("outputFormat") == "stream-json":
        return {"type": "result", "subtype": "success", "session_id": str(uuid4()), "result": prompt}
    if not prompt:
        return {"type": "result", "subtype": "success", "session_id": str(uuid4()), "result": ""}
    processor = opts.get("processor")
    if processor is None and opts.get("useDeepSeek"):
        processor = CodeProcessor()
    if processor is not None:
        result = await _maybe_await(processor.chat(prompt))
        text = result if isinstance(result, str) else getattr(result, "content", str(result))
    else:
        text = prompt
    return {"type": "result", "subtype": "success", "session_id": str(uuid4()), "result": text}


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value) or isinstance(value, asyncio.Future):
        return await value
    return value
