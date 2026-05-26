"""Structured replacement for the existing-secret confirmation step."""

from __future__ import annotations

from typing import Any

from ._shared import DEFAULT_SECRET_NAME, step_payload


async def CheckExistingSecretStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    secret_name = kwargs.get("secretName", DEFAULT_SECRET_NAME)
    return step_payload(
        "check-existing-secret",
        secretName=secret_name,
        secretExists=bool(kwargs.get("secretExists", False)),
        message=f"If `{secret_name}` already exists, reuse it instead of overwriting secrets from this shim.",
    )


__all__ = ["CheckExistingSecretStep"]
