"""Command metadata for `/rate-limit-options`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_path = Path(__file__).with_name("rate-limit-options.py")
_spec = importlib.util.spec_from_file_location("rate_limit_options_command_impl", _path)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
call = _module.call
getRateLimitOptions = _module.getRateLimitOptions

rateLimitOptions = {
    "type": "local",
    "name": "rate-limit-options",
    "description": "Choose what to do after a DeepSeek rate limit",
    "progressMessage": "loading rate limit options",
    "source": "builtin",
    "call": call,
}

default = rateLimitOptions
