from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from python_src.tools.path_utils import resolve_workspace_path


DEFAULT_CONFIG_PATH = ".deepseek_code_config.json"


def _config_path(path: str = DEFAULT_CONFIG_PATH, *, cwd: str | None = None) -> Path:
    return resolve_workspace_path(path, cwd=cwd)


def load_config(path: str = DEFAULT_CONFIG_PATH, *, cwd: str | None = None) -> dict[str, Any]:
    target = _config_path(path, cwd=cwd)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any], path: str = DEFAULT_CONFIG_PATH, *, cwd: str | None = None) -> Path:
    target = _config_path(path, cwd=cwd)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
