"""Validation helpers for keybindings.json."""

from __future__ import annotations

import re
from typing import Any

from .parser import chordToString, parseBindings, parseChord, parseKeystroke
from .reservedShortcuts import getReservedShortcuts, normalizeKeyForComparison

VALID_CONTEXTS = {
    "Global",
    "Chat",
    "Autocomplete",
    "Confirmation",
    "Help",
    "Transcript",
    "HistorySearch",
    "Task",
    "ThemePicker",
    "Scroll",
    "Settings",
    "Tabs",
    "Attachments",
    "Footer",
    "MessageSelector",
    "DiffDialog",
    "ModelPicker",
    "Select",
    "Plugin",
    "MessageActions",
}


def _warning(type_: str, severity: str, message: str, **kwargs: Any) -> dict[str, Any]:
    return {"type": type_, "severity": severity, "message": message, **{k: v for k, v in kwargs.items() if v is not None}}


def _is_block(block: Any) -> bool:
    return isinstance(block, dict) and isinstance(block.get("context"), str) and isinstance(block.get("bindings"), dict)


def _validate_keystroke(key: str) -> dict[str, Any] | None:
    for part in key.lower().split("+"):
        if not part.strip():
            return _warning("parse_error", "error", f'Empty key part in "{key}"', key=key, suggestion='Remove extra "+" characters')
    parsed = parseKeystroke(key)
    if not parsed.get("key") and not any(parsed.get(flag) for flag in ("ctrl", "alt", "shift", "meta", "super")):
        return _warning("parse_error", "error", f'Could not parse keystroke "{key}"', key=key)
    return None


def validateUserConfig(userBlocks: Any) -> list[dict[str, Any]]:
    if not isinstance(userBlocks, list):
        return [_warning("parse_error", "error", "keybindings.json must contain an array", suggestion="Wrap your bindings in [ ]")]
    warnings: list[dict[str, Any]] = []
    for index, block in enumerate(userBlocks):
        if not isinstance(block, dict):
            warnings.append(_warning("parse_error", "error", f"Keybinding block {index + 1} is not an object"))
            continue
        context = block.get("context")
        context_name = context if isinstance(context, str) else None
        if not isinstance(context, str):
            warnings.append(_warning("parse_error", "error", f'Keybinding block {index + 1} missing "context" field'))
        elif context not in VALID_CONTEXTS:
            warnings.append(_warning("invalid_context", "error", f'Unknown context "{context}"', context=context, suggestion="Valid contexts: " + ", ".join(sorted(VALID_CONTEXTS))))
        bindings = block.get("bindings")
        if not isinstance(bindings, dict):
            warnings.append(_warning("parse_error", "error", f'Keybinding block {index + 1} missing "bindings" field'))
            continue
        for key, action in bindings.items():
            key_error = _validate_keystroke(str(key))
            if key_error:
                key_error["context"] = context_name
                warnings.append(key_error)
            if action is not None and not isinstance(action, str):
                warnings.append(_warning("invalid_action", "error", f'Invalid action for "{key}": must be a string or null', key=key, context=context_name))
            elif isinstance(action, str) and action.startswith("command:"):
                if not re.match(r"^command:[a-zA-Z0-9:\-_]+$", action):
                    warnings.append(_warning("invalid_action", "warning", f'Invalid command binding "{action}" for "{key}"', key=key, context=context_name, action=action))
                if context_name and context_name != "Chat":
                    warnings.append(_warning("invalid_action", "warning", f'Command binding "{action}" must be in "Chat" context, not "{context_name}"', key=key, context=context_name, action=action, suggestion='Move this binding to a block with "context": "Chat"'))
            elif action == "voice:pushToTalk":
                ks = parseChord(str(key))[0]
                if not any(ks.get(flag) for flag in ("ctrl", "alt", "shift", "meta", "super")) and re.match(r"^[a-z]$", str(ks.get("key", ""))):
                    warnings.append(_warning("invalid_action", "warning", f'Binding "{key}" to voice:pushToTalk prints into the input during warmup', key=key, context=context_name, action=action))
    return warnings


def checkDuplicateKeysInJson(jsonString: str) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for match in re.finditer(r'"bindings"\s*:\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', jsonString):
        content = match.group(1)
        before = jsonString[: match.start()]
        ctx_match = re.search(r'"context"\s*:\s*"([^"]+)"[^{]*$', before)
        context = ctx_match.group(1) if ctx_match else "unknown"
        seen: dict[str, int] = {}
        for key_match in re.finditer(r'"([^"]+)"\s*:', content):
            key = key_match.group(1)
            seen[key] = seen.get(key, 0) + 1
            if seen[key] == 2:
                warnings.append(_warning("duplicate", "warning", f'Duplicate key "{key}" in {context} bindings', key=key, context=context, suggestion="JSON uses the last value; earlier values are ignored."))
    return warnings


def checkDuplicates(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    seen_by_context: dict[str, dict[str, Any]] = {}
    for block in blocks:
        context = str(block.get("context"))
        context_seen = seen_by_context.setdefault(context, {})
        for key, action in (block.get("bindings") or {}).items():
            normalized = normalizeKeyForComparison(str(key))
            existing = context_seen.get(normalized)
            if existing is not None and existing != action:
                warnings.append(_warning("duplicate", "warning", f'Duplicate binding "{key}" in {context} context', key=key, context=context, action=action or "null (unbind)", suggestion=f'Previously bound to "{existing}". Only the last binding will be used.'))
            context_seen[normalized] = action if action is not None else "null"
    return warnings


def checkReservedShortcuts(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    reserved = getReservedShortcuts()
    for binding in bindings:
        display = chordToString(binding.get("chord") or [])
        normalized = normalizeKeyForComparison(display)
        for item in reserved:
            if normalizeKeyForComparison(item["key"]) == normalized:
                warnings.append(_warning("reserved", item["severity"], f'"{display}" may not work: {item["reason"]}', key=display, context=binding.get("context"), action=binding.get("action")))
    return warnings


def validateBindings(userBlocks: Any, _parsedBindings: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    warnings = validateUserConfig(userBlocks)
    if isinstance(userBlocks, list) and all(_is_block(block) for block in userBlocks):
        warnings.extend(checkDuplicates(userBlocks))
        warnings.extend(checkReservedShortcuts(parseBindings(userBlocks)))
    seen: set[tuple[Any, Any, Any]] = set()
    unique: list[dict[str, Any]] = []
    for warning in warnings:
        key = (warning.get("type"), warning.get("key"), warning.get("context"))
        if key not in seen:
            seen.add(key)
            unique.append(warning)
    return unique


def formatWarning(warning: dict[str, Any]) -> str:
    icon = "ERROR" if warning.get("severity") == "error" else "WARN"
    message = f"{icon}: Keybinding {warning.get('severity')}: {warning.get('message')}"
    if warning.get("suggestion"):
        message += "\n  " + str(warning["suggestion"])
    return message


def formatWarnings(warnings: list[dict[str, Any]]) -> str:
    if not warnings:
        return ""
    errors = [w for w in warnings if w.get("severity") == "error"]
    warns = [w for w in warnings if w.get("severity") == "warning"]
    lines: list[str] = []
    if errors:
        lines.append(f"Found {len(errors)} keybinding error{'s' if len(errors) != 1 else ''}:")
        lines.extend(formatWarning(w) for w in errors)
    if warns:
        if lines:
            lines.append("")
        lines.append(f"Found {len(warns)} keybinding warning{'s' if len(warns) != 1 else ''}:")
        lines.extend(formatWarning(w) for w in warns)
    return "\n".join(lines)
