from __future__ import annotations

from typing import Any

from deepseek_code.core.tool_adapter import tools_to_deepseek
from deepseek_code.core.types import InternalMessage, InternalToolCall


class PromptAdapter:
    @staticmethod
    def from_claude(
        *,
        system: str | list[str] | None = None,
        messages: list[dict[str, Any]] | None = None,
    ) -> list[InternalMessage]:
        internal: list[InternalMessage] = []
        if system:
            text = "\n\n".join(system) if isinstance(system, list) else system
            internal.append(InternalMessage(role="system", content=text))
        for message in messages or []:
            role = message.get("role")
            if role not in {"system", "user", "assistant"}:
                continue
            internal.append(
                InternalMessage(
                    role=role,
                    content=PromptAdapter._strip_claude_content(message.get("content")),
                )
            )
        return internal

    @staticmethod
    def build_request(
        messages: list[InternalMessage],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
        max_tokens: int | None = None,
        temperature: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [PromptAdapter.message_to_wire(m) for m in messages],
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        converted_tools = tools_to_deepseek(tools)
        if converted_tools:
            payload["tools"] = converted_tools
        if extra:
            payload.update(extra)
        return payload

    @staticmethod
    def message_to_wire(message: InternalMessage) -> dict[str, Any]:
        wire: dict[str, Any] = {"role": message.role}
        if message.content is not None:
            wire["content"] = message.content
        if message.name:
            wire["name"] = message.name
        if message.tool_call_id:
            wire["tool_call_id"] = message.tool_call_id
        if message.tool_calls:
            wire["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments
                        if isinstance(call.arguments, str)
                        else __import__("json").dumps(call.arguments, ensure_ascii=False),
                    },
                }
                for call in message.tool_calls
            ]
        return wire

    @staticmethod
    def _strip_claude_content(content: Any) -> str | list[dict[str, Any]] | None:
        if isinstance(content, str) or content is None:
            return content
        if not isinstance(content, list):
            return str(content)
        converted: list[dict[str, Any]] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                converted.append({"type": "text", "text": block.get("text", "")})
            elif block_type == "image":
                source = block.get("source", {})
                url = source.get("url") or block.get("url")
                if url:
                    converted.append({"type": "image_url", "image_url": {"url": url}})
            elif block_type == "tool_result":
                converted.append({"type": "text", "text": str(block.get("content", ""))})
        return converted


def tool_calls_from_wire(raw_calls: list[dict[str, Any]] | None) -> list[InternalToolCall]:
    calls: list[InternalToolCall] = []
    for call in raw_calls or []:
        fn = call.get("function") or {}
        calls.append(
            InternalToolCall(
                id=call.get("id", ""),
                type=call.get("type", "function"),
                name=fn.get("name", ""),
                arguments=fn.get("arguments", ""),
            )
        )
    return calls
