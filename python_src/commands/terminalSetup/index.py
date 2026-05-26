"""Command metadata for `/terminal-setup`."""

from __future__ import annotations

from .terminalSetup import (
    call,
    getNativeCSIuTerminalDisplayName,
    hasUsedBackslashReturn,
    isShiftEnterKeyBindingInstalled,
    markBackslashReturnUsed,
    setupTerminal,
    shouldOfferTerminalSetup,
)

terminalSetup = {
    "type": "local",
    "name": "terminal-setup",
    "aliases": ["terminalSetup"],
    "description": "Configure terminal key bindings",
    "progressMessage": "setting up terminal",
    "source": "builtin",
    "call": call,
}

default = terminalSetup
