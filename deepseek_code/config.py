from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional at runtime
    load_dotenv = None


def _split_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_env_line(line: str) -> tuple[str, str] | None:
    line = line.strip().lstrip("\ufeff")
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    if "=" not in line:
        return None
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return key, value


def _candidate_env_files() -> list[Path]:
    explicit = os.getenv("DEEPSEEK_ENV_FILE")
    if explicit:
        return [Path(explicit).expanduser()]
    candidates: list[Path] = []
    cwd_env = Path.cwd() / ".env"
    repo_env = Path(__file__).resolve().parents[1] / ".env"
    for path in (cwd_env, repo_env):
        if path not in candidates:
            candidates.append(path)
    return candidates


def load_env_files() -> list[Path]:
    """Load `.env` values without requiring python-dotenv.

    Real environment variables win.  This keeps PowerShell overrides and CI
    secrets authoritative while allowing `python -m deepseek_code.cli` to work
    directly from a project `.env` file.
    """

    loaded: list[Path] = []
    if load_dotenv is not None:
        for path in _candidate_env_files():
            if path.exists():
                load_dotenv(path, override=False)
                loaded.append(path)
    for path in _candidate_env_files():
        if not path.exists():
            continue
        if path not in loaded:
            loaded.append(path)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            parsed = _parse_env_line(line)
            if parsed is None:
                continue
            key, value = parsed
            os.environ.setdefault(key, value)
    return loaded


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
        load_env_files()
        api_keys = _split_env("DEEPSEEK_API_KEYS")
        if not api_keys and os.getenv("DEEPSEEK_API_KEY"):
            api_keys = [os.getenv("DEEPSEEK_API_KEY", "").strip()]
        models = _split_env("DEEPSEEK_MODELS", os.getenv("DEFAULT_MODEL", "deepseek-chat"))
        default_model = os.getenv("DEFAULT_MODEL", models[0] if models else "deepseek-chat")
        endpoints = _split_env("DEEPSEEK_ENDPOINTS", "https://api.deepseek.com")
        return cls(
            api_keys=api_keys,
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
