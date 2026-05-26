"""Default keybindings for the Python runtime."""

from __future__ import annotations

import os
import platform
from typing import Any


def _feature_enabled(name: str) -> bool:
    env_name = "DEEPCODE_FEATURE_" + name.upper().replace("-", "_")
    return str(os.getenv(env_name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _get_platform() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system == "darwin":
        return "macos"
    return "linux"


IMAGE_PASTE_KEY = "alt+v" if _get_platform() == "windows" else "ctrl+v"
MODE_CYCLE_KEY = "meta+m" if _get_platform() == "windows" else "shift+tab"

DEFAULT_BINDINGS: list[dict[str, Any]] = [
    {
        "context": "Global",
        "bindings": {
            "ctrl+c": "app:interrupt",
            "ctrl+d": "app:exit",
            "ctrl+l": "app:redraw",
            "ctrl+t": "app:toggleTodos",
            "ctrl+o": "app:toggleTranscript",
            "ctrl+shift+o": "app:toggleTeammatePreview",
            "ctrl+r": "history:search",
        },
    },
    {
        "context": "Chat",
        "bindings": {
            "escape": "chat:cancel",
            "ctrl+x ctrl+k": "chat:killAgents",
            MODE_CYCLE_KEY: "chat:cycleMode",
            "meta+p": "chat:modelPicker",
            "meta+o": "chat:fastMode",
            "meta+t": "chat:thinkingToggle",
            "enter": "chat:submit",
            "up": "history:previous",
            "down": "history:next",
            "ctrl+_": "chat:undo",
            "ctrl+shift+-": "chat:undo",
            "ctrl+x ctrl+e": "chat:externalEditor",
            "ctrl+g": "chat:externalEditor",
            "ctrl+s": "chat:stash",
            IMAGE_PASTE_KEY: "chat:imagePaste",
        },
    },
    {"context": "Autocomplete", "bindings": {"tab": "autocomplete:accept", "escape": "autocomplete:dismiss", "up": "autocomplete:previous", "down": "autocomplete:next"}},
    {
        "context": "Settings",
        "bindings": {
            "escape": "confirm:no",
            "up": "select:previous",
            "down": "select:next",
            "k": "select:previous",
            "j": "select:next",
            "ctrl+p": "select:previous",
            "ctrl+n": "select:next",
            "space": "select:accept",
            "enter": "settings:close",
            "/": "settings:search",
            "r": "settings:retry",
        },
    },
    {
        "context": "Confirmation",
        "bindings": {
            "y": "confirm:yes",
            "n": "confirm:no",
            "enter": "confirm:yes",
            "escape": "confirm:no",
            "up": "confirm:previous",
            "down": "confirm:next",
            "tab": "confirm:nextField",
            "space": "confirm:toggle",
            "shift+tab": "confirm:cycleMode",
            "ctrl+e": "confirm:toggleExplanation",
            "ctrl+d": "permission:toggleDebug",
        },
    },
    {"context": "Tabs", "bindings": {"tab": "tabs:next", "shift+tab": "tabs:previous", "right": "tabs:next", "left": "tabs:previous"}},
    {"context": "Transcript", "bindings": {"ctrl+e": "transcript:toggleShowAll", "ctrl+c": "transcript:exit", "escape": "transcript:exit", "q": "transcript:exit"}},
    {"context": "HistorySearch", "bindings": {"ctrl+r": "historySearch:next", "escape": "historySearch:accept", "tab": "historySearch:accept", "ctrl+c": "historySearch:cancel", "enter": "historySearch:execute"}},
    {"context": "Task", "bindings": {"ctrl+b": "task:background"}},
    {"context": "ThemePicker", "bindings": {"ctrl+t": "theme:toggleSyntaxHighlighting"}},
    {
        "context": "Scroll",
        "bindings": {
            "pageup": "scroll:pageUp",
            "pagedown": "scroll:pageDown",
            "wheelup": "scroll:lineUp",
            "wheeldown": "scroll:lineDown",
            "ctrl+home": "scroll:top",
            "ctrl+end": "scroll:bottom",
            "ctrl+shift+c": "selection:copy",
            "cmd+c": "selection:copy",
        },
    },
    {"context": "Help", "bindings": {"escape": "help:dismiss"}},
    {"context": "Attachments", "bindings": {"right": "attachments:next", "left": "attachments:previous", "backspace": "attachments:remove", "delete": "attachments:remove", "down": "attachments:exit", "escape": "attachments:exit"}},
    {"context": "Footer", "bindings": {"up": "footer:up", "ctrl+p": "footer:up", "down": "footer:down", "ctrl+n": "footer:down", "right": "footer:next", "left": "footer:previous", "enter": "footer:openSelected", "escape": "footer:clearSelection"}},
    {
        "context": "MessageSelector",
        "bindings": {
            "up": "messageSelector:up",
            "down": "messageSelector:down",
            "k": "messageSelector:up",
            "j": "messageSelector:down",
            "ctrl+p": "messageSelector:up",
            "ctrl+n": "messageSelector:down",
            "ctrl+up": "messageSelector:top",
            "shift+up": "messageSelector:top",
            "meta+up": "messageSelector:top",
            "shift+k": "messageSelector:top",
            "ctrl+down": "messageSelector:bottom",
            "shift+down": "messageSelector:bottom",
            "meta+down": "messageSelector:bottom",
            "shift+j": "messageSelector:bottom",
            "enter": "messageSelector:select",
        },
    },
    {"context": "DiffDialog", "bindings": {"escape": "diff:dismiss", "left": "diff:previousSource", "right": "diff:nextSource", "up": "diff:previousFile", "down": "diff:nextFile", "enter": "diff:viewDetails"}},
    {"context": "ModelPicker", "bindings": {"left": "modelPicker:decreaseEffort", "right": "modelPicker:increaseEffort"}},
    {"context": "Select", "bindings": {"up": "select:previous", "down": "select:next", "j": "select:next", "k": "select:previous", "ctrl+n": "select:next", "ctrl+p": "select:previous", "enter": "select:accept", "escape": "select:cancel"}},
    {"context": "Plugin", "bindings": {"space": "plugin:toggle", "i": "plugin:install"}},
]

if _feature_enabled("KAIROS") or _feature_enabled("KAIROS_BRIEF"):
    DEFAULT_BINDINGS[0]["bindings"]["ctrl+shift+b"] = "app:toggleBrief"
if _feature_enabled("QUICK_SEARCH"):
    DEFAULT_BINDINGS[0]["bindings"].update(
        {
            "ctrl+shift+f": "app:globalSearch",
            "cmd+shift+f": "app:globalSearch",
            "ctrl+shift+p": "app:quickOpen",
            "cmd+shift+p": "app:quickOpen",
        }
    )
if _feature_enabled("TERMINAL_PANEL"):
    DEFAULT_BINDINGS[0]["bindings"]["meta+j"] = "app:toggleTerminal"
if _feature_enabled("MESSAGE_ACTIONS"):
    DEFAULT_BINDINGS.append(
        {
            "context": "MessageActions",
            "bindings": {
                "up": "messageActions:prev",
                "down": "messageActions:next",
                "k": "messageActions:prev",
                "j": "messageActions:next",
                "meta+up": "messageActions:top",
                "meta+down": "messageActions:bottom",
                "super+up": "messageActions:top",
                "super+down": "messageActions:bottom",
                "shift+up": "messageActions:prevUser",
                "shift+down": "messageActions:nextUser",
                "escape": "messageActions:escape",
                "ctrl+c": "messageActions:ctrlc",
                "enter": "messageActions:enter",
                "c": "messageActions:c",
                "p": "messageActions:p",
            },
        }
    )
if _feature_enabled("VOICE_MODE"):
    DEFAULT_BINDINGS[1]["bindings"]["space"] = "voice:pushToTalk"
