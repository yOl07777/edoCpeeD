from __future__ import annotations


BLACK_CIRCLE = "*"
BLOCKQUOTE_BAR = "|"
BRIDGE_FAILED_INDICATOR = "x"
BRIDGE_READY_INDICATOR = "ok"
BRIDGE_SPINNER_FRAMES = ["-", "\\", "|", "/"]
BULLET_OPERATOR = "-"
CHANNEL_ARROW = "->"
DIAMOND_FILLED = "*"
DIAMOND_OPEN = "<>"
DOWN_ARROW = "v"
EFFORT_LOW = "low"
EFFORT_MEDIUM = "medium"
EFFORT_HIGH = "high"
EFFORT_MAX = "xhigh"
FLAG_ICON = "flag"
FORK_GLYPH = "fork"
HEAVY_HORIZONTAL = "-"
INJECTED_ARROW = "=>"
LIGHTNING_BOLT = "fast"
PAUSE_ICON = "pause"
PLAY_ICON = "play"
REFERENCE_MARK = "#"
REFRESH_ARROW = "refresh"
TEARDROP_ASTERISK = "*"
UP_ARROW = "^"


__all__ = [name for name in globals() if name.isupper()]
