"""Open or create the keybindings configuration file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from python_src.keybindings.loadUserBindings import getKeybindingsPath, isKeybindingCustomizationEnabled
from python_src.keybindings.template import generateKeybindingsTemplate


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    if not isKeybindingCustomizationEnabled():
        return {"type": "text", "value": "Keybinding customization is not enabled. This feature is currently in preview."}
    path = Path(getKeybindingsPath())
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not existed:
        path.write_text(generateKeybindingsTemplate(), encoding="utf-8")
    return {
        "type": "text",
        "value": f"{'Opened' if existed else 'Created'} {path}." + ("" if existed else " Template written."),
    }
