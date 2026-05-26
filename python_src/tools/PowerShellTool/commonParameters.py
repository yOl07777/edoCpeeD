"""PowerShell common parameter metadata."""

from __future__ import annotations

COMMON_SWITCHES = {
    "Verbose",
    "Debug",
    "ErrorAction",
    "WarningAction",
    "InformationAction",
    "ErrorVariable",
    "WarningVariable",
    "InformationVariable",
    "OutVariable",
    "OutBuffer",
    "PipelineVariable",
    "WhatIf",
    "Confirm",
}
COMMON_VALUE_PARAMS = {
    "ErrorAction",
    "WarningAction",
    "InformationAction",
    "ErrorVariable",
    "WarningVariable",
    "InformationVariable",
    "OutVariable",
    "OutBuffer",
    "PipelineVariable",
}
COMMON_PARAMETERS = COMMON_SWITCHES | COMMON_VALUE_PARAMS

__all__ = ["COMMON_PARAMETERS", "COMMON_SWITCHES", "COMMON_VALUE_PARAMS"]
