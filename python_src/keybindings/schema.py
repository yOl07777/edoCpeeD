"""Schema-like constants for keybinding configuration."""

from __future__ import annotations

from typing import Any

from .defaultBindings import DEFAULT_BINDINGS

KEYBINDING_CONTEXTS = sorted({block["context"] for block in DEFAULT_BINDINGS})
KEYBINDING_ACTIONS = sorted(
    {
        action
        for block in DEFAULT_BINDINGS
        for action in (block.get("bindings") or {}).values()
        if isinstance(action, str)
    }
)

KEYBINDING_CONTEXT_DESCRIPTIONS = {
    "Global": "Always available application shortcuts.",
    "Chat": "Prompt input and conversation shortcuts.",
    "Autocomplete": "Autocomplete menu navigation.",
    "Settings": "Settings panel navigation.",
    "Confirmation": "Confirmation and permission dialogs.",
    "Tabs": "Tab navigation.",
    "Transcript": "Transcript reading view.",
    "HistorySearch": "History search modal.",
    "Task": "Foreground task controls.",
    "ThemePicker": "Theme picker controls.",
    "Scroll": "Scrollable region controls.",
    "Help": "Help view controls.",
    "Attachments": "Attachment list controls.",
    "Footer": "Footer indicator navigation.",
    "MessageSelector": "Message selection dialog.",
    "DiffDialog": "Diff dialog navigation.",
    "ModelPicker": "Model picker controls.",
    "Select": "Generic select component controls.",
    "Plugin": "Plugin dialog actions.",
    "MessageActions": "Message actions menu.",
}

KeybindingBlockSchema: dict[str, Any] = {
    "type": "object",
    "required": ["context", "bindings"],
    "properties": {
        "context": {"type": "string", "enum": KEYBINDING_CONTEXTS},
        "bindings": {
            "type": "object",
            "additionalProperties": {"anyOf": [{"type": "string", "enum": KEYBINDING_ACTIONS}, {"type": "null"}]},
        },
    },
}

KeybindingsSchema: dict[str, Any] = {
    "type": "object",
    "required": ["bindings"],
    "properties": {"bindings": {"type": "array", "items": KeybindingBlockSchema}},
}
