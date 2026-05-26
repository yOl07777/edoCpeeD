"""Local MCP client helpers for the Python migration.

The TypeScript runtime starts SDK transports and remote clients here.  The
Python migration keeps the public boundary but makes it deterministic and safe:
callers can pass lightweight client objects, and configured servers are exposed
as structured "not connected" records instead of spawning processes.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Awaitable, Callable

from .config import getAllMcpConfigs, getMcpServerSignature, isMcpServerDisabled

connectToServer: Any = None
fetchCommandsForClient: Any = None
fetchResourcesForClient: Any = None
fetchToolsForClient: Any = None

_SERVER_CACHE: dict[str, dict[str, Any]] = {}
_AUTH_CACHE: dict[str, Any] = {}


class McpAuthError(Exception):
    """Raised when a local MCP client reports an authentication failure."""

    def __init__(self, serverName: str, message: str | None = None) -> None:
        self.serverName = serverName
        super().__init__(message or f'MCP server "{serverName}" needs authentication')


class McpToolCallError_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS(Exception):
    """Raised when an MCP tool result is explicitly marked as an error."""

    def __init__(
        self,
        message: str,
        telemetryMessage: str | None = None,
        mcpMeta: dict[str, Any] | None = None,
    ) -> None:
        self.telemetryMessage = telemetryMessage or message
        self.mcpMeta = mcpMeta or {}
        super().__init__(message)


def _first_arg(args: tuple[Any, ...], kwargs: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in kwargs:
            return kwargs[name]
    return args[0] if args else default


def _stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _stable(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_stable(v) for v in value]
    return value


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value) or hasattr(value, "__await__"):
        return await value
    return value


def _server_name(server: Any, fallback: str = "mcp") -> str:
    if isinstance(server, dict):
        return str(server.get("name") or server.get("serverName") or fallback)
    return str(getattr(server, "name", None) or getattr(server, "serverName", None) or fallback)


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if "text" in content:
            return str(content["text"])
        if "data" in content:
            return str(content["data"])
    return json.dumps(content, ensure_ascii=False, sort_keys=True)


async def areMcpConfigsEqual(*args: Any, **kwargs: Any) -> bool:
    left = _first_arg(args, kwargs, "left", "a", "configA", default={})
    right = args[1] if len(args) > 1 else kwargs.get("right", kwargs.get("b", kwargs.get("configB", {})))
    return _stable(left) == _stable(right)


async def callIdeRpc(*args: Any, **kwargs: Any) -> dict[str, Any]:
    method = str(kwargs.get("method") or (args[0] if args else ""))
    params = kwargs.get("params") if "params" in kwargs else (args[1] if len(args) > 1 else {})
    return {"ok": False, "method": method, "params": params or {}, "reason": "IDE RPC is not connected in Python shim"}


async def callMCPToolWithUrlElicitationRetry(*args: Any, **kwargs: Any) -> Any:
    client = kwargs.get("client") or (args[0] if args else None)
    request = kwargs.get("request") or kwargs.get("tool") or (args[1] if len(args) > 1 else {})
    if client is not None and callable(getattr(client, "callTool", None)):
        return await _maybe_await(client.callTool(request))
    if client is not None and callable(getattr(client, "call_tool", None)):
        return await _maybe_await(client.call_tool(request))
    name = request.get("name") if isinstance(request, dict) else str(request)
    return {"content": [{"type": "text", "text": f"MCP tool {name} is not connected"}], "isError": True}


async def clearMcpAuthCache(*args: Any, **kwargs: Any) -> dict[str, Any]:
    server = kwargs.get("serverName") or (args[0] if args else None)
    if server:
        removed = _AUTH_CACHE.pop(str(server), None) is not None
        return {"cleared": removed, "serverName": str(server)}
    count = len(_AUTH_CACHE)
    _AUTH_CACHE.clear()
    return {"cleared": count}


async def clearServerCache(*args: Any, **kwargs: Any) -> dict[str, Any]:
    server = kwargs.get("serverName") or (args[0] if args else None)
    if server:
        removed = _SERVER_CACHE.pop(str(server), None) is not None
        return {"cleared": removed, "serverName": str(server)}
    count = len(_SERVER_CACHE)
    _SERVER_CACHE.clear()
    return {"cleared": count}


async def createClaudeAiProxyFetch(*args: Any, **kwargs: Any) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _fetch(url: str, init: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "ok": False,
            "status": 501,
            "url": url,
            "init": init or {},
            "reason": "Claude.ai proxy fetch is disabled in DeepSeek Python migration",
        }

    return _fetch


async def ensureConnectedClient(*args: Any, **kwargs: Any) -> dict[str, Any]:
    server = _first_arg(args, kwargs, "server", "config", default={})
    name = str(kwargs.get("serverName") or _server_name(server))
    cached = _SERVER_CACHE.get(name)
    if cached:
        return dict(cached)
    config = dict(server) if isinstance(server, dict) else {"name": name}
    state = {
        "name": name,
        "type": "disabled" if isMcpServerDisabled(name) else "disconnected",
        "config": config,
        "client": kwargs.get("client"),
        "tools": [],
        "commands": [],
        "resources": [],
    }
    _SERVER_CACHE[name] = state
    return dict(state)


async def getMcpServerConnectionBatchSize(*args: Any, **kwargs: Any) -> int:
    value = kwargs.get("batchSize") or os.getenv("DEEPCODE_MCP_CONNECTION_BATCH_SIZE")
    try:
        return max(1, int(value))
    except Exception:
        return 5


async def getMcpToolsCommandsAndResources(*args: Any, **kwargs: Any) -> dict[str, Any]:
    configs = kwargs.get("configs")
    if configs is None:
        configs = (await getAllMcpConfigs()).get("servers", {})
    result = {"clients": {}, "tools": [], "commands": [], "resources": [], "errors": []}
    for name, config in dict(configs or {}).items():
        connection = await ensureConnectedClient(config, serverName=name)
        result["clients"][name] = {k: v for k, v in connection.items() if k != "client"}
        if isMcpServerDisabled(name):
            continue
        for item in connection.get("tools", []) or []:
            result["tools"].append({"serverName": name, **(item if isinstance(item, dict) else {"name": str(item)})})
        for item in connection.get("commands", []) or []:
            result["commands"].append({"serverName": name, **(item if isinstance(item, dict) else {"name": str(item)})})
        for item in connection.get("resources", []) or []:
            result["resources"].append({"serverName": name, **(item if isinstance(item, dict) else {"uri": str(item)})})
    return result


async def getServerCacheKey(*args: Any, **kwargs: Any) -> str:
    name = kwargs.get("serverName") or (args[0] if args else "mcp")
    config = kwargs.get("config") or (args[1] if len(args) > 1 else {})
    signature = getMcpServerSignature(config) if isinstance(config, dict) else None
    return f"{name}:{signature or json.dumps(_stable(config), ensure_ascii=False, sort_keys=True)}"


async def inferCompactSchema(*args: Any, **kwargs: Any) -> dict[str, Any]:
    schema = _first_arg(args, kwargs, "schema", "inputSchema", default={})
    if not isinstance(schema, dict):
        return {"type": "object", "properties": {}}
    return {"type": schema.get("type", "object"), "properties": schema.get("properties", {}), "required": schema.get("required", [])}


async def isMcpSessionExpiredError(*args: Any, **kwargs: Any) -> bool:
    error = _first_arg(args, kwargs, "error", default=None)
    code = getattr(error, "code", None)
    message = str(error)
    return code == 404 and ('"code":-32001' in message or '"code": -32001' in message or "Session not found" in message)


async def mcpToolInputToAutoClassifierInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    tool_input = _first_arg(args, kwargs, "input", "toolInput", default={})
    return {"text": json.dumps(tool_input, ensure_ascii=False, sort_keys=True), "source": "mcp_tool_input"}


async def prefetchAllMcpResources(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = await getMcpToolsCommandsAndResources(configs=kwargs.get("configs"))
    return {"resources": state["resources"], "count": len(state["resources"])}


async def processMCPResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await transformMCPResult(*args, **kwargs)


async def reconnectMcpServerImpl(*args: Any, **kwargs: Any) -> dict[str, Any]:
    name = str(kwargs.get("serverName") or (args[0] if args else "mcp"))
    await clearServerCache(name)
    config = kwargs.get("config") or {}
    connection = await ensureConnectedClient(config, serverName=name, client=kwargs.get("client"))
    connection["reconnected"] = True
    return connection


async def setupSdkMcpClients(*args: Any, **kwargs: Any) -> dict[str, Any]:
    configs = kwargs.get("configs") or (args[0] if args else {})
    clients = {
        name: {"name": name, "type": "sdk", "status": "available"}
        for name, config in dict(configs or {}).items()
        if isinstance(config, dict) and config.get("type") == "sdk"
    }
    return {"clients": clients, "count": len(clients)}


async def transformMCPResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = _first_arg(args, kwargs, "result", default={})
    if result is None:
        result = {}
    if not isinstance(result, dict):
        result = {"content": [{"type": "text", "text": str(result)}]}
    content = await transformResultContent(result.get("content", []))
    output = {**result, "content": content, "text": "\n".join(item["text"] for item in content if item.get("text"))}
    if result.get("isError"):
        raise McpToolCallError_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS(output["text"] or "MCP tool call failed", mcpMeta={"_meta": result.get("_meta", {})})
    return output


async def transformResultContent(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    content = _first_arg(args, kwargs, "content", default=[])
    if isinstance(content, (str, dict)):
        content = [content]
    transformed: list[dict[str, Any]] = []
    for item in content or []:
        if isinstance(item, dict):
            kind = str(item.get("type") or ("text" if "text" in item else "json"))
            transformed.append({**item, "type": kind, "text": _content_text(item)})
        else:
            transformed.append({"type": "text", "text": str(item)})
    return transformed


async def wrapFetchWithTimeout(*args: Any, **kwargs: Any) -> Callable[..., Awaitable[Any]]:
    fetch = kwargs.get("fetch") or kwargs.get("fetchFn") or (args[0] if args else None)
    timeout_ms = int(kwargs.get("timeoutMs") or (args[1] if len(args) > 1 else 30000))

    async def _wrapped(*fetch_args: Any, **fetch_kwargs: Any) -> Any:
        if not callable(fetch):
            return {"ok": False, "status": 501, "reason": "No fetch function provided"}
        return await asyncio.wait_for(_maybe_await(fetch(*fetch_args, **fetch_kwargs)), timeout=timeout_ms / 1000)

    return _wrapped


__all__ = [
    "McpAuthError",
    "McpToolCallError_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS",
    "areMcpConfigsEqual",
    "callIdeRpc",
    "callMCPToolWithUrlElicitationRetry",
    "clearMcpAuthCache",
    "clearServerCache",
    "createClaudeAiProxyFetch",
    "ensureConnectedClient",
    "getMcpServerConnectionBatchSize",
    "getMcpToolsCommandsAndResources",
    "getServerCacheKey",
    "inferCompactSchema",
    "isMcpSessionExpiredError",
    "mcpToolInputToAutoClassifierInput",
    "prefetchAllMcpResources",
    "processMCPResult",
    "reconnectMcpServerImpl",
    "setupSdkMcpClients",
    "transformMCPResult",
    "transformResultContent",
    "wrapFetchWithTimeout",
]
