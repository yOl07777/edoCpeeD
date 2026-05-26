from __future__ import annotations

from typing import Any


def normalize_option(option: Any, index: int = 0, selected: bool = False) -> dict[str, Any]:
    if isinstance(option, dict):
        value = option.get("value", option.get("id", option.get("label", index)))
        label = option.get("label", value)
        disabled = bool(option.get("disabled", False))
    else:
        value = option
        label = option
        disabled = False
    return {
        "index": index,
        "value": value,
        "label": str(label),
        "disabled": disabled,
        "selected": selected,
    }


def normalize_options(options: Any, selected: Any = None) -> list[dict[str, Any]]:
    selected_values = set(selected if isinstance(selected, list) else ([] if selected is None else [selected]))
    rows: list[dict[str, Any]] = []
    for index, option in enumerate(options or []):
        value = option.get("value", option.get("id")) if isinstance(option, dict) else option
        rows.append(normalize_option(option, index, value in selected_values))
    return rows


def clamp_index(index: int, count: int) -> int:
    if count <= 0:
        return 0
    return max(0, min(index, count - 1))


def select_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload
