"""Command metadata for `/tasks`."""

from __future__ import annotations

from .tasks import call, formatTaskSummary, getTaskSummary


tasks = {
    "type": "local-jsx",
    "name": "tasks",
    "description": "Manage background tasks",
    "supportsNonInteractive": True,
    "call": call,
}

default = tasks

__all__ = ["call", "default", "formatTaskSummary", "getTaskSummary", "tasks"]
