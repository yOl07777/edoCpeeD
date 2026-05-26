from __future__ import annotations

import os
import time
from typing import Any, Callable

from python_src.utils.config import (
    getCurrentProjectConfig,
    getGlobalConfig,
    saveCurrentProjectConfig,
    saveGlobalConfig,
)
from python_src.utils.settings.settings import (
    getInitialSettings,
    getSettingsForSource,
    hasSkipDangerousModePermissionPrompt,
    updateSettingsForSource,
)


def is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_first_party() -> bool:
    return (os.getenv("DEEPSEEK_API_PROVIDER") or os.getenv("API_PROVIDER") or "firstParty") == "firstParty"


def is_pro_subscriber() -> bool:
    return is_truthy(os.getenv("DEEPCODE_IS_PRO") or os.getenv("IS_PRO_SUBSCRIBER"))


def is_paid_subscriber() -> bool:
    return is_pro_subscriber() or is_truthy(os.getenv("DEEPCODE_IS_MAX") or os.getenv("DEEPCODE_IS_TEAM_PREMIUM"))


def legacy_model_remap_enabled() -> bool:
    return not is_truthy(os.getenv("DEEPCODE_DISABLE_LEGACY_MODEL_REMAP"))


def opus_1m_merge_enabled() -> bool:
    return is_truthy(os.getenv("DEEPCODE_OPUS_1M_MERGE_ENABLED"))


async def user_settings() -> dict[str, Any]:
    parsed = await getSettingsForSource("user")
    return parsed.get("settings", parsed)


async def local_settings() -> dict[str, Any]:
    parsed = await getSettingsForSource("local")
    return parsed.get("settings", parsed)


async def update_user_settings(updates: dict[str, Any]) -> dict[str, Any]:
    return await updateSettingsForSource("user", updates)


async def update_local_settings(updates: dict[str, Any]) -> dict[str, Any]:
    return await updateSettingsForSource("local", updates)


async def mutate_global_config(mutator: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    return await saveGlobalConfig(mutator)


async def mutate_project_config(mutator: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    return await saveCurrentProjectConfig(mutator)


async def get_global_config() -> dict[str, Any]:
    return await getGlobalConfig()


async def get_project_config() -> dict[str, Any]:
    return await getCurrentProjectConfig()


async def get_merged_settings() -> dict[str, Any]:
    return await getInitialSettings()


async def has_skip_dangerous_prompt() -> bool:
    return await hasSkipDangerousModePermissionPrompt()


def now_ms() -> int:
    return int(time.time() * 1000)
