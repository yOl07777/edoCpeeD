"""Prompt helpers for ScheduleCronTool."""

from __future__ import annotations

import os
from typing import Any

CRON_CREATE_TOOL_NAME = "cron_create"
CRON_LIST_TOOL_NAME = "cron_list"
CRON_DELETE_TOOL_NAME = "cron_delete"
DEFAULT_MAX_AGE_DAYS = 30
CRON_LIST_DESCRIPTION = "List in-memory scheduled task records."
CRON_DELETE_DESCRIPTION = "Delete an in-memory scheduled task record by id."


async def isDurableCronEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    return os.getenv("DEEPCODE_DURABLE_CRON", "").lower() in {"1", "true", "yes", "on"}


async def isKairosCronEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    return os.getenv("DEEPCODE_KAIROS_CRON", "").lower() in {"1", "true", "yes", "on"}


async def buildCronCreateDescription(*args: Any, **kwargs: Any) -> str:
    max_age = int(kwargs.get("maxAgeDays") or kwargs.get("max_age_days") or DEFAULT_MAX_AGE_DAYS)
    return (
        "Create an in-memory scheduled task record with a name, prompt, and human schedule or RRULE. "
        f"Records are local dry-run state; default max age is {max_age} days."
    )


async def buildCronCreatePrompt(*args: Any, **kwargs: Any) -> str:
    return f"Use {CRON_CREATE_TOOL_NAME} to record a local scheduled task. It does not create an external job."


async def buildCronListPrompt(*args: Any, **kwargs: Any) -> str:
    return f"Use {CRON_LIST_TOOL_NAME} to inspect local scheduled task records, optionally filtered by status."


async def buildCronDeletePrompt(*args: Any, **kwargs: Any) -> str:
    return f"Use {CRON_DELETE_TOOL_NAME} with the exact cron_id returned by {CRON_LIST_TOOL_NAME}."


__all__ = [
    "CRON_CREATE_TOOL_NAME",
    "CRON_DELETE_DESCRIPTION",
    "CRON_DELETE_TOOL_NAME",
    "CRON_LIST_DESCRIPTION",
    "CRON_LIST_TOOL_NAME",
    "DEFAULT_MAX_AGE_DAYS",
    "buildCronCreateDescription",
    "buildCronCreatePrompt",
    "buildCronDeletePrompt",
    "buildCronListPrompt",
    "isDurableCronEnabled",
    "isKairosCronEnabled",
]
