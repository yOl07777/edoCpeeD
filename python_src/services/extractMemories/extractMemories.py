"""Background persistent-memory extraction."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Awaitable, Callable

from python_src.bootstrap.state import getIsRemoteMode
from python_src.memdir.memoryScan import formatMemoryManifest, scanMemoryFiles
from python_src.memdir.paths import getAutoMemPath, isAutoMemPath, isAutoMemoryEnabled
from python_src.services.extractMemories.prompts import buildExtractAutoOnlyPrompt, buildExtractCombinedPrompt


AppendSystemMessage = Callable[[dict[str, Any]], None]
Extractor = Callable[[dict[str, Any], AppendSystemMessage | None], Awaitable[dict[str, Any] | None]]

_extractor: Extractor | None = None
_in_flight: set[asyncio.Task[Any]] = set()


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _message_type(message: dict[str, Any]) -> str | None:
    return message.get("type") or message.get("role")


def _content_blocks(message: dict[str, Any]) -> list[Any]:
    content = (message.get("message") or {}).get("content", message.get("content"))
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def _is_model_visible(message: dict[str, Any]) -> bool:
    return _message_type(message) in {"user", "assistant"}


def _count_visible_since(messages: list[dict[str, Any]], since_uuid: str | None) -> int:
    if not since_uuid:
        return sum(1 for msg in messages if _is_model_visible(msg))
    found = False
    count = 0
    for msg in messages:
        if not found:
            if msg.get("uuid") == since_uuid:
                found = True
            continue
        if _is_model_visible(msg):
            count += 1
    return count if found else sum(1 for msg in messages if _is_model_visible(msg))


def _written_file_path(block: dict[str, Any]) -> str | None:
    if block.get("type") not in {"tool_use", "tool_call"}:
        return None
    name = block.get("name") or (block.get("function") or {}).get("name")
    if name not in {"Edit", "Write", "FileEdit", "FileWrite"}:
        return None
    input_value = block.get("input") or block.get("arguments") or {}
    return input_value.get("file_path") if isinstance(input_value, dict) and isinstance(input_value.get("file_path"), str) else None


def _has_memory_writes_since(messages: list[dict[str, Any]], since_uuid: str | None) -> bool:
    found = since_uuid is None
    for msg in messages:
        if not found:
            if msg.get("uuid") == since_uuid:
                found = True
            continue
        if _message_type(msg) != "assistant":
            continue
        for block in _content_blocks(msg):
            if isinstance(block, dict):
                path = _written_file_path(block)
                if path and isAutoMemPath(path):
                    return True
    return False


def _extract_written_paths(messages: list[dict[str, Any]]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for msg in messages:
        if _message_type(msg) != "assistant":
            continue
        for block in _content_blocks(msg):
            if isinstance(block, dict):
                path = _written_file_path(block)
                if path and path not in seen:
                    seen.add(path)
                    paths.append(path)
    return paths


def _deny(reason: str) -> dict[str, Any]:
    return {"behavior": "deny", "message": reason, "decisionReason": {"type": "other", "reason": reason}}


def createAutoMemCanUseTool(memoryDir: str, *_: Any, **__: Any) -> Callable[[dict[str, Any] | Any, dict[str, Any]], Awaitable[dict[str, Any]]]:
    async def can_use_tool(tool: dict[str, Any] | Any, input: dict[str, Any] | None = None) -> dict[str, Any]:
        data = input or {}
        name = tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None)
        if name in {"REPL", "Read", "Grep", "Glob"}:
            return {"behavior": "allow", "updatedInput": data}
        if name in {"Bash", "run_shell", "PowerShell"}:
            command = str(data.get("command") or "")
            lowered = command.strip().lower()
            read_only_prefixes = ("ls", "dir", "find", "grep", "cat", "type", "stat", "wc", "head", "tail", "get-childitem", "select-string")
            if lowered.startswith(read_only_prefixes) and not any(token in lowered for token in [">", ">>", " rm ", "del ", "remove-item", "mv ", "move-item"]):
                return {"behavior": "allow", "updatedInput": data}
            return _deny("Only read-only shell commands are permitted while extracting memories.")
        if name in {"Edit", "Write", "FileEdit", "FileWrite"}:
            file_path = data.get("file_path")
            if isinstance(file_path, str) and isAutoMemPath(file_path):
                return {"behavior": "allow", "updatedInput": data}
        return _deny(f"Only memory-safe tools are allowed; writes must stay within {memoryDir}.")

    return can_use_tool


def initExtractMemories(*_: Any, **__: Any) -> None:
    last_memory_uuid: str | None = None
    in_progress = False
    pending: tuple[dict[str, Any], AppendSystemMessage | None] | None = None

    async def run_extraction(context: dict[str, Any], append: AppendSystemMessage | None = None, trailing: bool = False) -> dict[str, Any] | None:
        nonlocal last_memory_uuid, in_progress, pending
        messages = list(context.get("messages") or [])
        memory_dir = getAutoMemPath()
        new_count = _count_visible_since(messages, last_memory_uuid)
        if _has_memory_writes_since(messages, last_memory_uuid):
            if messages and messages[-1].get("uuid"):
                last_memory_uuid = messages[-1]["uuid"]
            return {"status": "skipped", "reason": "direct_memory_write", "messageCount": new_count}

        in_progress = True
        try:
            existing = await formatMemoryManifest(await scanMemoryFiles(memory_dir))
            prompt = await buildExtractCombinedPrompt(new_count, existing, False) if _truthy(os.getenv("DEEPSEEK_TEAM_MEMORY")) else await buildExtractAutoOnlyPrompt(new_count, existing, False)
            runner = context.get("runForkedAgent") or (context.get("toolUseContext") or {}).get("runForkedAgent")
            if callable(runner):
                result = runner(
                    {
                        "prompt": prompt,
                        "querySource": "extract_memories",
                        "forkLabel": "extract_memories",
                        "canUseTool": createAutoMemCanUseTool(memory_dir),
                        "maxTurns": 5,
                    }
                )
                if hasattr(result, "__await__"):
                    result = await result
            else:
                result = {"messages": [], "totalUsage": {"input_tokens": 0, "output_tokens": 0}}
            if messages and messages[-1].get("uuid"):
                last_memory_uuid = messages[-1]["uuid"]
            written = _extract_written_paths(list((result or {}).get("messages") or []))
            memory_paths = [p for p in written if Path(p).name != "MEMORY.md"]
            if append and memory_paths:
                append({"type": "system", "level": "info", "message": f"Saved memories: {', '.join(memory_paths)}", "paths": memory_paths})
            return {"status": "completed", "prompt": prompt, "messageCount": new_count, "writtenPaths": written, "memoryPaths": memory_paths, "result": result}
        finally:
            in_progress = False
            if pending:
                next_context, next_append = pending
                pending = None
                await run_extraction(next_context, next_append, trailing=True)

    async def execute(context: dict[str, Any], append: AppendSystemMessage | None = None) -> dict[str, Any] | None:
        nonlocal pending
        tool_context = context.get("toolUseContext") or {}
        if tool_context.get("agentId"):
            return {"status": "skipped", "reason": "subagent"}
        if not _truthy(os.getenv("DEEPSEEK_EXTRACT_MEMORIES")):
            return {"status": "skipped", "reason": "gate_disabled"}
        if not isAutoMemoryEnabled() or getIsRemoteMode():
            return {"status": "skipped", "reason": "memory_disabled_or_remote"}
        if in_progress:
            pending = (context, append)
            return {"status": "coalesced"}
        return await run_extraction(context, append)

    global _extractor
    _extractor = execute


async def executeExtractMemories(context: dict[str, Any] | None = None, appendSystemMessage: AppendSystemMessage | None = None, *_: Any, **__: Any) -> dict[str, Any] | None:
    if _extractor is None:
        initExtractMemories()
    assert _extractor is not None
    task = asyncio.create_task(_extractor(context or {}, appendSystemMessage))
    _in_flight.add(task)
    try:
        return await task
    finally:
        _in_flight.discard(task)


async def drainPendingExtraction(timeoutMs: int | None = None, *_: Any, **__: Any) -> None:
    if not _in_flight:
        return
    timeout = (timeoutMs or 60_000) / 1000
    try:
        await asyncio.wait_for(asyncio.gather(*list(_in_flight), return_exceptions=True), timeout=timeout)
    except TimeoutError:
        return


__all__ = ["createAutoMemCanUseTool", "drainPendingExtraction", "executeExtractMemories", "initExtractMemories"]
