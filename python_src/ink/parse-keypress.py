from __future__ import annotations

from typing import Any

INITIAL_STATE = {"provider": "deepseek", "mode": "ground"}
DECRPM_STATUS = {"notRecognized": 0, "set": 1, "reset": 2, "permanentlySet": 3, "permanentlyReset": 4}
nonAlphanumericKeys = {
    "\r": "return",
    "\n": "return",
    "\t": "tab",
    "\x1b": "escape",
    "\x7f": "backspace",
    "\x1b[A": "up",
    "\x1b[B": "down",
    "\x1b[C": "right",
    "\x1b[D": "left",
}


def _parse_one(sequence: str) -> dict[str, Any]:
    name = nonAlphanumericKeys.get(sequence, sequence)
    ctrl = len(sequence) == 1 and 0 < ord(sequence) < 27
    if ctrl:
        name = chr(ord(sequence) + 96)
    return {"kind": "key", "sequence": sequence, "name": name, "ctrl": ctrl, "meta": False, "shift": False}


async def parseMultipleKeypresses(*args: Any, **kwargs: Any) -> Any:
    data = str(args[0] if args else kwargs.get("input", ""))
    keys: list[dict[str, Any]] = []
    i = 0
    while i < len(data):
        if data.startswith("\x1b[<", i):
            end_press = data.find("M", i)
            end_release = data.find("m", i)
            ends = [value for value in (end_press, end_release) if value >= 0]
            if ends:
                end = min(ends)
                seq = data[i : end + 1]
                body = seq[3:-1]
                parts = body.split(";")
                if len(parts) == 3:
                    keys.append({"kind": "mouse", "sequence": seq, "button": int(parts[0]), "col": int(parts[1]), "row": int(parts[2]), "action": "press" if seq.endswith("M") else "release"})
                    i = end + 1
                    continue
        matched = None
        for seq in sorted(nonAlphanumericKeys, key=len, reverse=True):
            if data.startswith(seq, i):
                matched = seq
                break
        matched = matched or data[i]
        keys.append(_parse_one(matched))
        i += len(matched)
    return {"keys": keys, "state": dict(INITIAL_STATE)}
