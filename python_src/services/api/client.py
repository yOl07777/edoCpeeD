from __future__ import annotations

from deepseek_code.client import DeepSeekClient, DeepSeekLoadBalancer
from deepseek_code.config import DeepSeekConfig


def get_deepseek_config(
    *,
    api_key: str | None = None,
    model: str | None = None,
    endpoint: str | None = None,
) -> DeepSeekConfig:
    return DeepSeekConfig.from_env().with_overrides(
        api_key=api_key,
        model=model,
        endpoint=endpoint,
    )


def get_deepseek_client(
    *,
    api_key: str | None = None,
    model: str | None = None,
    endpoint: str | None = None,
) -> DeepSeekClient:
    config = get_deepseek_config(api_key=api_key, model=model, endpoint=endpoint)
    return DeepSeekClient(config, load_balancer=DeepSeekLoadBalancer(config))
