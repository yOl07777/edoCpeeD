from __future__ import annotations

from typing import Any


LOGO_TEXT = "DeepSeek Code"
SHORT_LOGO_TEXT = "DS Code"
ASTERISK_FRAMES = ("*", "+", "x", ".")

DEFAULT_FEED_MESSAGES = (
    "DeepSeek Code ready",
    "Use /help for commands",
    "Workspace tools are available after approval",
)


def logo_payload(component: str, **values: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(values)
    return payload


def first_options(args: tuple[Any, ...]) -> dict[str, Any]:
    return args[0] if args and isinstance(args[0], dict) else {}


def scalar_arg(args: tuple[Any, ...], default: Any = None) -> Any:
    return args[0] if args and not isinstance(args[0], dict) else default


def option(args: tuple[Any, ...], kwargs: dict[str, Any], name: str, default: Any = None) -> Any:
    if name in kwargs:
        return kwargs[name]
    return first_options(args).get(name, default)


def frame_glyph(value: Any = 0) -> str:
    return ASTERISK_FRAMES[frame_index(value) % len(ASTERISK_FRAMES)]


def frame_index(value: Any = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_feed_items(items: Any = None) -> list[dict[str, Any]]:
    if items is None:
        iterable: Any = DEFAULT_FEED_MESSAGES
    elif isinstance(items, dict):
        iterable = items.get("items") or items.get("messages") or [items]
    elif isinstance(items, (str, bytes)):
        iterable = [items.decode() if isinstance(items, bytes) else items]
    else:
        iterable = items

    rows: list[dict[str, Any]] = []
    for index, item in enumerate(iterable or []):
        if isinstance(item, dict):
            text = str(item.get("text") or item.get("message") or item.get("title") or "")
            rows.append(
                {
                    "type": "feed_item",
                    "index": index,
                    "text": text,
                    "tone": item.get("tone", "info"),
                    "priority": item.get("priority", index),
                }
            )
        else:
            rows.append({"type": "feed_item", "index": index, "text": str(item), "tone": "info", "priority": index})
    return rows


def visible_by_seen_count(args: tuple[Any, ...], kwargs: dict[str, Any], *, default: bool = True, max_seen: int = 3) -> bool:
    opts = first_options(args)
    if "enabled" in kwargs or "enabled" in opts:
        enabled = option(args, kwargs, "enabled", default)
    else:
        enabled = default
    if not enabled or option(args, kwargs, "dismissed", False):
        return False
    try:
        seen_count = int(option(args, kwargs, "seenCount", option(args, kwargs, "seen_count", 0)) or 0)
    except (TypeError, ValueError):
        seen_count = 0
    return seen_count < max_seen


def notice_text(args: tuple[Any, ...], kwargs: dict[str, Any], fallback: str) -> str:
    return str(option(args, kwargs, "message", option(args, kwargs, "text", fallback)))
