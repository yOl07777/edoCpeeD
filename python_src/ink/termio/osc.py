from __future__ import annotations

import base64
import os
from typing import Any

OSC_PREFIX: str = "\x1b]"
ST: str = "\x1b\\"
OSC: str = OSC_PREFIX
ITERM2: str = "1337"
PROGRESS: str = "9;4"
LINK_END: str = f"{OSC_PREFIX}8;;{ST}"
CLEAR_TERMINAL_TITLE: str = f"{OSC_PREFIX}0;{ST}"
CLEAR_ITERM2_PROGRESS: str = f"{OSC_PREFIX}{PROGRESS};0;0{ST}"
CLEAR_TAB_STATUS: str = f"{OSC_PREFIX}21337;clear{ST}"

async def _resetLinuxCopyCache(*args: Any, **kwargs: Any) -> Any:
    return {"provider": "deepseek", "reset": True}

async def getClipboardPath(*args: Any, **kwargs: Any) -> Any:
    return os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY") or "terminal"

async def link(*args: Any, **kwargs: Any) -> Any:
    url = str(args[0] if args else kwargs.get("url", ""))
    text = str(args[1] if len(args) > 1 else kwargs.get("text", ""))
    params = kwargs.get("params", "")
    param_text = params if isinstance(params, str) else ":".join(f"{k}={v}" for k, v in params.items())
    return f"{OSC_PREFIX}8;{param_text};{url}{ST}{text}{LINK_END}"

async def osc(*args: Any, **kwargs: Any) -> Any:
    command = str(args[0] if args else kwargs.get("command", ""))
    value = str(args[1] if len(args) > 1 else kwargs.get("value", ""))
    separator = ";" if value or not command.endswith(";") else ""
    return f"{OSC_PREFIX}{command}{separator}{value}{ST}"

async def parseOSC(*args: Any, **kwargs: Any) -> Any:
    sequence = str(args[0] if args else kwargs.get("sequence", ""))
    body = sequence
    if body.startswith(OSC_PREFIX):
        body = body[len(OSC_PREFIX):]
    if body.endswith(ST):
        body = body[:-len(ST)]
    elif body.endswith("\x07"):
        body = body[:-1]
    command, _, value = body.partition(";")
    if command in ("0", "2"):
        return {"type": "title", "action": {"type": "windowTitle" if command == "2" else "both", "title": value}}
    if command == "1":
        return {"type": "title", "action": {"type": "iconName", "name": value}}
    if command == "8":
        parts = value.split(";", 1)
        url = parts[1] if len(parts) > 1 else ""
        return {"type": "link", "action": {"type": "start" if url else "end", "url": url}}
    if command == "21337":
        return {"type": "tabStatus", "action": {"status": value or None}}
    return {"type": "unknown", "sequence": sequence}

async def parseOscColor(*args: Any, **kwargs: Any) -> Any:
    value = str(args[0] if args else kwargs.get("value", ""))
    if value.startswith("#") and len(value) == 7:
        return {"type": "rgb", "r": int(value[1:3], 16), "g": int(value[3:5], 16), "b": int(value[5:7], 16)}
    if value.startswith("rgb:"):
        parts = value[4:].split("/")
        if len(parts) == 3:
            return {"type": "rgb", "r": int(parts[0][:2], 16), "g": int(parts[1][:2], 16), "b": int(parts[2][:2], 16)}
    return {"type": "default"}

async def setClipboard(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"{OSC_PREFIX}52;c;{encoded}{ST}"

async def supportsTabStatus(*args: Any, **kwargs: Any) -> Any:
    term_program = kwargs.get("term_program", os.environ.get("TERM_PROGRAM", ""))
    return str(term_program).lower() in {"vscode", "cursor", "windsurf", "iterm.app"}

async def tabStatus(*args: Any, **kwargs: Any) -> Any:
    status = str(args[0] if args else kwargs.get("status", ""))
    return f"{OSC_PREFIX}21337;{status}{ST}"

async def tmuxLoadBuffer(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    name = str(kwargs.get("name", "deepcode"))
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"\x1bPtmux;\x1b]52;{name};{encoded}\x07\x1b\\"

async def wrapForMultiplexer(*args: Any, **kwargs: Any) -> Any:
    sequence = str(args[0] if args else kwargs.get("sequence", ""))
    multiplexer = str(kwargs.get("multiplexer", os.environ.get("TERM", ""))).lower()
    if "tmux" in multiplexer:
        return "\x1bPtmux;" + sequence.replace("\x1b", "\x1b\x1b") + "\x1b\\"
    return sequence
