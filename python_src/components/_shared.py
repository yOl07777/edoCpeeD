from __future__ import annotations

from pathlib import Path
from typing import Any


def component_payload(component: str, **values: Any) -> dict[str, Any]:
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


def normalize_items(items: Any = None, *, text_key: str = "text") -> list[dict[str, Any]]:
    if items is None:
        iterable: Any = []
    elif isinstance(items, dict):
        iterable = items.get("items") or items.get("messages") or items.get("tasks") or [items]
    elif isinstance(items, (str, bytes)):
        iterable = [items.decode() if isinstance(items, bytes) else items]
    else:
        iterable = items

    rows: list[dict[str, Any]] = []
    for index, item in enumerate(iterable or []):
        if isinstance(item, dict):
            text = str(item.get(text_key) or item.get("message") or item.get("title") or item.get("name") or "")
            row = dict(item)
            row.update({"index": index, text_key: text})
            rows.append(row)
        else:
            rows.append({"index": index, text_key: str(item)})
    return rows


def redact(value: Any, *, keep: int = 4) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    if len(text) <= keep:
        return "*" * len(text)
    return f"{'*' * max(4, len(text) - keep)}{text[-keep:]}"


def percent(numerator: Any, denominator: Any) -> float:
    try:
        den = float(denominator)
        if den <= 0:
            return 0.0
        return round((float(numerator) / den) * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def path_label(value: Any) -> str:
    if value is None:
        return ""
    try:
        return str(Path(str(value)))
    except (TypeError, ValueError):
        return str(value)
