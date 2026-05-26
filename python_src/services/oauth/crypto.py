"""OAuth PKCE helpers ported from ``src/services/oauth/crypto.ts``."""

from __future__ import annotations

import base64
import hashlib
import os


def _base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def generateCodeVerifier() -> str:
    return _base64_url_encode(os.urandom(32))


def generateCodeChallenge(verifier: str) -> str:
    return _base64_url_encode(hashlib.sha256(verifier.encode("utf-8")).digest())


def generateState() -> str:
    return _base64_url_encode(os.urandom(32))


__all__ = ["generateCodeChallenge", "generateCodeVerifier", "generateState"]
