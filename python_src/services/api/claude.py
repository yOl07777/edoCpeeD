from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from deepseek_code.client.deepseek_client import DeepSeekClient
from deepseek_code.config import DeepSeekConfig
from deepseek_code.core.code_processor import CodeProcessor
from deepseek_code.core.prompt_builder import PromptAdapter
from deepseek_code.core.response_adapter import ResponseAdapter
from deepseek_code.core.types import InternalResponse


def build_deepseek_messages(
    *,
    system: str | list[str] | None = None,
    messages: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    internal = PromptAdapter.from_claude(system=system, messages=messages)
    return [PromptAdapter.message_to_wire(message) for message in internal]


async def query_model_without_streaming(
    *,
    prompt: str,
    model: str | None = None,
    system_prompt: str | None = None,
    api_key: str | None = None,
    endpoint: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> InternalResponse:
    config = DeepSeekConfig.from_env().with_overrides(
        api_key=api_key,
        model=model,
        endpoint=endpoint,
    )
    async with DeepSeekClient(config) as client:
        processor = CodeProcessor(
            client,
            model=model or config.default_model,
            **({"system_prompt": system_prompt} if system_prompt else {}),
        )
        return await processor.run(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )


async def query_model_streaming(
    *,
    prompt: str,
    model: str | None = None,
    system_prompt: str | None = None,
    api_key: str | None = None,
    endpoint: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> AsyncIterator[str]:
    config = DeepSeekConfig.from_env().with_overrides(
        api_key=api_key,
        model=model,
        endpoint=endpoint,
    )
    async with DeepSeekClient(config) as client:
        processor = CodeProcessor(
            client,
            model=model or config.default_model,
            **({"system_prompt": system_prompt} if system_prompt else {}),
        )
        async for delta in processor.stream_text(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        ):
            if isinstance(delta, str):
                yield delta


def parse_deepseek_response(response: dict[str, Any]) -> InternalResponse:
    return ResponseAdapter.from_completion(response)
