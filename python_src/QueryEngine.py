"""QueryEngine compatibility wrapper backed by DeepSeek CodeProcessor."""

from __future__ import annotations

from typing import Any

from deepseek_code.config import DeepSeekConfig


class QueryEngine:
    def __init__(
        self,
        client: Any | None = None,
        *,
        model: str | None = None,
        tool_registry: Any | None = None,
        system_prompt: str | None = None,
        config: DeepSeekConfig | None = None,
        **kwargs: Any,
    ) -> None:
        self.client = client
        self.config = config or DeepSeekConfig.from_env()
        self.model = model or self.config.default_model
        self.tool_registry = tool_registry
        self.system_prompt = system_prompt
        self.kwargs = kwargs
        self._processor: Any | None = None
        self._owned_client: Any | None = None

    async def _get_processor(self) -> Any:
        if self._processor is not None:
            return self._processor
        from deepseek_code.client.deepseek_client import DeepSeekClient
        from deepseek_code.core.code_processor import CodeProcessor

        if self.client is None:
            self._owned_client = DeepSeekClient(self.config)
            self.client = await self._owned_client.__aenter__()
        kwargs: dict[str, Any] = {"model": self.model, "tool_registry": self.tool_registry}
        if self.system_prompt:
            kwargs["system_prompt"] = self.system_prompt
        self._processor = CodeProcessor(self.client, **kwargs)
        return self._processor

    async def query(self, prompt: str, **kwargs: Any) -> Any:
        processor = await self._get_processor()
        return await processor.run(prompt, **kwargs)

    async def stream(self, prompt: str, **kwargs: Any) -> Any:
        processor = await self._get_processor()
        async for delta in processor.stream_text(prompt, **kwargs):
            yield delta

    async def close(self) -> None:
        if self._owned_client is not None:
            await self._owned_client.__aexit__(None, None, None)
            self._owned_client = None
            self.client = None

    async def __aenter__(self) -> "QueryEngine":
        await self._get_processor()
        return self

    async def __aexit__(self, *_exc: Any) -> None:
        await self.close()


__all__ = ["QueryEngine"]
