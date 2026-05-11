from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional at runtime
    load_dotenv = None


def _split_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class DeepSeekConfig:
    api_keys: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=lambda: ["deepseek-chat"])
    endpoints: list[str] = field(default_factory=lambda: ["https://api.deepseek.com"])
    balance_strategy: str = "round_robin"
    default_model: str = "deepseek-chat"
    timeout_seconds: float = 120.0
    max_retries: int = 3
    cooldown_seconds: float = 30.0
    max_concurrency: int = 8

    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        if load_dotenv is not None:
            load_dotenv()
        models = _split_env("DEEPSEEK_MODELS", os.getenv("DEFAULT_MODEL", "deepseek-chat"))
        default_model = os.getenv("DEFAULT_MODEL", models[0] if models else "deepseek-chat")
        endpoints = _split_env("DEEPSEEK_ENDPOINTS", "https://api.deepseek.com")
        return cls(
            api_keys=_split_env("DEEPSEEK_API_KEYS"),
            models=models or [default_model],
            endpoints=endpoints,
            balance_strategy=os.getenv("DEEPSEEK_BALANCE_STRATEGY", "round_robin"),
            default_model=default_model,
            timeout_seconds=float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "120")),
            max_retries=int(os.getenv("DEEPSEEK_MAX_RETRIES", "3")),
            cooldown_seconds=float(os.getenv("DEEPSEEK_COOLDOWN_SECONDS", "30")),
            max_concurrency=int(os.getenv("DEEPSEEK_MAX_CONCURRENCY", "8")),
        )

    def with_overrides(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str | None = None,
    ) -> "DeepSeekConfig":
        return DeepSeekConfig(
            api_keys=[api_key] if api_key else self.api_keys,
            models=[model] if model else self.models,
            endpoints=[endpoint.rstrip("/")] if endpoint else self.endpoints,
            balance_strategy=self.balance_strategy,
            default_model=model or self.default_model,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            cooldown_seconds=self.cooldown_seconds,
            max_concurrency=self.max_concurrency,
        )
