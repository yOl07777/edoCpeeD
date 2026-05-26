"""Constrained Language Mode type helpers for PowerShell."""

from __future__ import annotations

from typing import Any

CLM_ALLOWED_TYPES = {
    "bool",
    "boolean",
    "byte",
    "char",
    "datetime",
    "decimal",
    "double",
    "guid",
    "hashtable",
    "int",
    "int16",
    "int32",
    "int64",
    "long",
    "pscustomobject",
    "regex",
    "single",
    "string",
    "timespan",
    "uint16",
    "uint32",
    "uint64",
    "xml",
}


async def normalizeTypeName(*args: Any, **kwargs: Any) -> str:
    value = str(args[0] if args else kwargs.get("typeName") or kwargs.get("type_name") or "")
    value = value.strip().strip("[]")
    for prefix in ("System.", "system.", "Microsoft.PowerShell.Commands."):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    return value.lower()


async def isClmAllowedType(*args: Any, **kwargs: Any) -> bool:
    return await normalizeTypeName(*args, **kwargs) in CLM_ALLOWED_TYPES


__all__ = ["CLM_ALLOWED_TYPES", "isClmAllowedType", "normalizeTypeName"]
