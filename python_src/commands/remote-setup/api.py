"""Local DeepSeek-compatible helpers for the `/web-setup` command.

The original TypeScript module posts a GitHub token to Claude's CCR backend and
creates a hosted Claude environment.  The Python migration keeps the public
shape but avoids Claude-only network calls.  It returns explicit local status
objects that callers can render or test without leaking credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal, TypedDict


ImportTokenErrorKind = Literal["not_signed_in", "invalid_token", "server", "network", "unsupported"]


class ImportTokenError(TypedDict, total=False):
    kind: ImportTokenErrorKind
    status: int
    message: str


class ImportTokenResult(TypedDict):
    github_username: str


class ImportGithubTokenOk(TypedDict):
    ok: Literal[True]
    result: ImportTokenResult


class ImportGithubTokenErr(TypedDict):
    ok: Literal[False]
    error: ImportTokenError


@dataclass(frozen=True)
class RedactedGithubToken:
    """Wrap a GitHub token so ordinary stringification never exposes it."""

    _value: str

    def reveal(self) -> str:
        return self._value

    def __str__(self) -> str:
        return "[REDACTED:gh-token]"

    def __repr__(self) -> str:
        return "[REDACTED:gh-token]"

    def toJSON(self) -> str:
        return "[REDACTED:gh-token]"


def _has_deepseek_credentials() -> bool:
    return bool(
        os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEYS")
        or os.environ.get("DEEPSEEK_ACCESS_TOKEN")
    )


async def importGithubToken(
    token: RedactedGithubToken,
) -> ImportGithubTokenOk | ImportGithubTokenErr:
    """Validate the call shape without uploading the token anywhere.

    DeepSeek's public API does not provide Claude's CCR GitHub-token import
    endpoint.  Returning an explicit unsupported result is safer than silently
    pretending that remote web setup succeeded.
    """

    raw = token.reveal().strip()
    if not raw:
        return {"ok": False, "error": {"kind": "invalid_token"}}
    if not _has_deepseek_credentials():
        return {"ok": False, "error": {"kind": "not_signed_in"}}
    return {
        "ok": False,
        "error": {
            "kind": "unsupported",
            "message": "DeepSeek Code does not upload GitHub tokens from this local shim.",
        },
    }


async def createDefaultEnvironment(*_: Any, **__: Any) -> bool:
    """Best-effort hosted environment creation placeholder.

    There is no DeepSeek equivalent of Claude's hosted code environment in this
    migration layer, so the operation is a harmless no-op.
    """

    return False


async def isSignedIn() -> bool:
    """Return whether local DeepSeek credentials appear to be configured."""

    return _has_deepseek_credentials()


def getCodeWebUrl() -> str:
    """Return the DeepSeek Code web destination used in local instructions."""

    return os.environ.get("DEEPSEEK_CODE_WEB_URL", "https://chat.deepseek.com")


__all__ = [
    "ImportGithubTokenErr",
    "ImportGithubTokenOk",
    "ImportTokenError",
    "ImportTokenResult",
    "RedactedGithubToken",
    "createDefaultEnvironment",
    "getCodeWebUrl",
    "importGithubToken",
    "isSignedIn",
]
