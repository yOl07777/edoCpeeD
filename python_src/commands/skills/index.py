"""Command metadata for `/skills`."""

from __future__ import annotations

from .skills import call, formatSkillSummary, getSkillSummary


skills = {
    "type": "local-jsx",
    "name": "skills",
    "description": "Show loaded project and plugin skills",
    "supportsNonInteractive": True,
    "call": call,
}

default = skills

__all__ = ["call", "default", "formatSkillSummary", "getSkillSummary", "skills"]
