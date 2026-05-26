"""Local `/version` command."""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Any


def _runtime_version() -> str:
    configured = os.getenv("DEEPCODE_VERSION") or os.getenv("DEEPSEEK_CODE_VERSION")
    if configured:
        return configured
    try:
        return package_version("deepseek-code")
    except PackageNotFoundError:
        return "0.0.0-dev"


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    build_time = os.getenv("DEEPCODE_BUILD_TIME") or os.getenv("DEEPSEEK_CODE_BUILD_TIME")
    value = f"{_runtime_version()} (built {build_time})" if build_time else _runtime_version()
    return {"type": "text", "value": value}


version_command = {
    "type": "local",
    "name": "version",
    "description": "Print the version this session is running",
    "isEnabled": lambda: os.getenv("USER_TYPE") == "ant" or os.getenv("DEEPSEEK_SHOW_VERSION_COMMAND") == "1",
    "supportsNonInteractive": True,
    "call": call,
}

default = version_command
