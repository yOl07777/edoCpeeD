"""Command metadata for `/usage`."""

from __future__ import annotations

from .usage import call, formatUsageSummary, getUsageSummary


usage = {
    "type": "local-jsx",
    "name": "usage",
    "description": "Show DeepSeek usage for this session",
    "supportsNonInteractive": True,
    "call": call,
}

default = usage

__all__ = ["call", "default", "formatUsageSummary", "getUsageSummary", "usage"]
