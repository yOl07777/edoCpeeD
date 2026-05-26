"""Command metadata for `/remote-env`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_path = Path(__file__).with_name("remote-env.py")
_spec = importlib.util.spec_from_file_location("remote_env_command_impl", _path)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
call = _module.call

remoteEnv = {
    "type": "local",
    "name": "remote-env",
    "description": "Show safe remote environment details",
    "progressMessage": "reading remote environment",
    "source": "builtin",
    "call": call,
}

default = remoteEnv
