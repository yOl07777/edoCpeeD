from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from deepseek_code.core.prompt_builder import PromptAdapter
from deepseek_code.core.response_adapter import ResponseAdapter, StreamingToolCallAccumulator
from deepseek_code.core.tool_adapter import ToolRegistry, tool_result_message
from deepseek_code.core.types import InternalMessage, InternalResponse, InternalStreamDelta

if TYPE_CHECKING:
    from deepseek_code.client.deepseek_client import DeepSeekClient

DEFAULT_SYSTEM_PROMPT = (
    "You are DeepSeek Code, a concise coding assistant. "
    "Help with code generation, analysis, refactoring, and debugging. "
    "Use tools when available and return clear, actionable answers."
)


class ToolRoundLimitExceeded(RuntimeError):
    """Raised when a turn keeps requesting tools after the configured limit."""


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
        self._repair_tool_call_sequence()
        start_index = len(self.messages)
        self.messages.append(InternalMessage(role="user", content=prompt))
        try:
            for _ in range(max_tool_rounds + 1):
                self._repair_tool_call_sequence()
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
            raise ToolRoundLimitExceeded(f"Maximum tool rounds exceeded ({max_tool_rounds}).")
        except Exception:
            del self.messages[start_index:]
            raise

    async def stream_text(
        self,
        prompt: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        max_tool_rounds: int = 5,
        max_tokens: int | None = None,
        temperature: float | None = None,
        tool_events: bool = False,
    ) -> AsyncIterator[str | InternalStreamDelta]:
        self._repair_tool_call_sequence()
        start_index = len(self.messages)
        self.messages.append(InternalMessage(role="user", content=prompt))
        try:
            for _ in range(max_tool_rounds + 1):
                self._repair_tool_call_sequence()
                request = PromptAdapter.build_request(
                    self.messages,
                    model=self.model,
                    tools=tools,
                    stream=True,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text_parts: list[str] = []
                reasoning_parts: list[str] = []
                tool_accumulator = StreamingToolCallAccumulator()
                async for chunk in self.client.stream(request):
                    raw_delta = ((chunk.get("choices") or [{}])[0].get("delta") or {})
                    tool_accumulator.add_delta(raw_delta.get("tool_calls"))
                    delta = ResponseAdapter.from_stream_chunk(chunk)
                    if delta.reasoning_content:
                        reasoning_parts.append(delta.reasoning_content)
                    if delta.content:
                        text_parts.append(delta.content)
                        yield delta.content
                tool_calls = [call for call in tool_accumulator.complete_calls() if call.id and call.name]
                self.messages.append(
                    InternalMessage(
                        role="assistant",
                        content="".join(text_parts),
                        tool_calls=tool_calls,
                        reasoning_content="".join(reasoning_parts) or None,
                    )
                )
                if not tool_calls:
                    return
                for call in tool_calls:
                    if tool_events:
                        yield InternalStreamDelta(tool_calls=[call], finish_reason="tool_call_started")
                    self.messages.append(await self.tool_registry.call(call))
                    if tool_events:
                        yield InternalStreamDelta(tool_calls=[call], finish_reason="tool_call_finished")
            raise ToolRoundLimitExceeded(f"Maximum tool rounds exceeded ({max_tool_rounds}).")
        except Exception:
            del self.messages[start_index:]
            raise

    def _repair_tool_call_sequence(self) -> None:
        repaired: list[InternalMessage] = []
        index = 0
        while index < len(self.messages):
            message = self.messages[index]
            if message.role == "tool":
                index += 1
                continue
            if message.role != "assistant" or not message.tool_calls:
                repaired.append(message)
                index += 1
                continue

            valid_calls = [call for call in message.tool_calls if call.id and call.name]
            message.tool_calls = valid_calls
            repaired.append(message)
            expected_ids = [call.id for call in valid_calls]
            seen: set[str] = set()
            index += 1
            while index < len(self.messages) and self.messages[index].role == "tool":
                tool_message = self.messages[index]
                if tool_message.tool_call_id in expected_ids and tool_message.tool_call_id not in seen:
                    repaired.append(tool_message)
                    seen.add(tool_message.tool_call_id or "")
                index += 1
            for tool_call_id in expected_ids:
                if tool_call_id not in seen:
                    repaired.append(
                        tool_result_message(
                            tool_call_id,
                            {
                                "ok": False,
                                "error": "Tool result was missing from local history; inserted a protocol repair message.",
                            },
                        )
                    )
        self.messages = repaired
