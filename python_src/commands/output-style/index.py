"""Deprecated /output-style command metadata."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_command_module() -> Any:
    path = Path(__file__).with_name("output-style.py")
    spec = importlib.util.spec_from_file_location("python_src.commands.output_style.output_style", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load output-style command from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


default = {
    "type": "local-jsx",
    "name": "output-style",
    "description": "Deprecated: use /config to change output style",
    "isHidden": True,
    "load": _load_command_module,
}
