"""Command metadata for `/keybindings`."""

from __future__ import annotations

from python_src.keybindings.loadUserBindings import isKeybindingCustomizationEnabled

from .keybindings import call

keybindings = {
    "name": "keybindings",
    "description": "Open or create your keybindings configuration file",
    "isEnabled": isKeybindingCustomizationEnabled,
    "supportsNonInteractive": False,
    "type": "local",
    "call": call,
}

default = keybindings
