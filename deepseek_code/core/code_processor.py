from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from deepseek_code.client.deepseek_client import DeepSeekClient
from deepseek_code.core.prompt_builder import PromptAdapter
from deepseek_code.core.response_adapter import ResponseAdapter, StreamingToolCallAccumulator
from deepseek_code.core.tool_adapter import ToolRegistry
from deepseek_code.core.types import InternalMessage, InternalResponse, InternalStreamDelta

DEFAULT_SYSTEM_PROMPT = (
    "You are DeepSeek Code, a concise coding assistant. "
    "Help with code generation, analysis, refactoring, and debugging. "
    "Use tools when available and return clear, actionable answers."
)


class CodeProcessor:
    def __init__(
        self,
        client: DeepSeekClient,
        *,
        model: str,
        tool_registry: ToolRegistry | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        self.client = client
        self.model = model
        self.tool_registry = tool_registry or ToolRegistry()
        self.messages: list[InternalMessage] = [InternalMessage(role="system", content=system_prompt)]

    async def run(
        self,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        max_tool_rounds: int = 5,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> InternalResponse:
        self.messages.append(InternalMessage(role="user", content=prompt))
        for _ in range(max_tool_rounds + 1):
            request = PromptAdapter.build_request(
                self.messages,
                model=self.model,
                tools=tools,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            response = ResponseAdapter.from_completion(await self.client.complete(request))
            self.messages.append(response.message)
            if not response.message.tool_calls:
                return response
            for call in response.message.tool_calls:
                self.messages.append(await self.tool_registry.call(call))
        raise RuntimeError("Maximum tool rounds exceeded.")

    async def stream_text(
        self,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str | InternalStreamDelta]:
        self.messages.append(InternalMessage(role="user", content=prompt))
        request = PromptAdapter.build_request(
            self.messages,
            model=self.model,
            tools=tools,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text_parts: list[str] = []
        tool_accumulator = StreamingToolCallAccumulator()
        async for chunk in self.client.stream(request):
            raw_delta = ((chunk.get("choices") or [{}])[0].get("delta") or {})
            tool_accumulator.add_delta(raw_delta.get("tool_calls"))
            delta = ResponseAdapter.from_stream_chunk(chunk)
            if delta.content:
                text_parts.append(delta.content)
                yield delta.content
        tool_calls = tool_accumulator.complete_calls()
        self.messages.append(
            InternalMessage(role="assistant", content="".join(text_parts), tool_calls=tool_calls)
        )
