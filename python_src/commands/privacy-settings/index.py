"""Command metadata for `/privacy-settings`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_path = Path(__file__).with_name("privacy-settings.py")
_spec = importlib.util.spec_from_file_location("privacy_settings_command_impl", _path)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
call = _module.call

privacySettings = {
    "type": "local",
    "name": "privacy-settings",
    "description": "Review and manage local privacy settings",
    "progressMessage": "opening privacy settings",
    "source": "builtin",
    "call": call,
}

default = privacySettings
