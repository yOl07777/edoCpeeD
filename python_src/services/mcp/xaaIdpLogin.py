"""Local XAA IdP login cache for the Python migration."""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

ID_TOKEN_EXPIRY_BUFFER_S = 60


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _cache_path() -> Path:
    return _config_home() / "mcp_xaa_idp.json"


def _read_cache() -> dict[str, Any]:
    try:
        data = json.loads(_cache_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_cache(data: dict[str, Any]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def issuerKey(issuer: str) -> str:
    try:
        parsed = urlparse(str(issuer))
        return parsed._replace(netloc=parsed.netloc.lower(), path=parsed.path.rstrip("/")).geturl()
    except Exception:
        return str(issuer).rstrip("/")


def _jwt_exp(jwt: str) -> int | None:
    try:
        payload = jwt.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        exp = decoded.get("exp")
        return int(exp) if exp is not None else None
    except Exception:
        return None


async def isXaaEnabled(*args: Any, **kwargs: Any) -> bool:
    return str(os.getenv("DEEPCODE_ENABLE_XAA") or os.getenv("DEEPSEEK_ENABLE_XAA") or "").lower() in {"1", "true", "yes", "on"}


async def getXaaIdpSettings(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    raw = os.getenv("DEEPCODE_XAA_IDP") or os.getenv("DEEPSEEK_XAA_IDP")
    if raw:
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else None
        except Exception:
            return {"issuer": raw}
    issuer = os.getenv("DEEPCODE_XAA_IDP_ISSUER") or os.getenv("DEEPSEEK_XAA_IDP_ISSUER")
    if not issuer:
        return None
    settings: dict[str, Any] = {"issuer": issuer}
    if os.getenv("DEEPCODE_XAA_IDP_CLIENT_ID"):
        settings["clientId"] = os.getenv("DEEPCODE_XAA_IDP_CLIENT_ID")
    return settings


async def getCachedIdpIdToken(*args: Any, **kwargs: Any) -> str | None:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    entry = (_read_cache().get("tokens") or {}).get(issuerKey(issuer))
    if not isinstance(entry, dict):
        return None
    if int(entry.get("expiresAt", 0)) <= int(time.time() * 1000) + ID_TOKEN_EXPIRY_BUFFER_S * 1000:
        return None
    return str(entry.get("idToken") or "") or None


async def saveIdpIdTokenFromJwt(*args: Any, **kwargs: Any) -> int:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    token = str(kwargs.get("idToken") or (args[1] if len(args) > 1 else ""))
    expires_at = (_jwt_exp(token) or int(time.time()) + 3600) * 1000
    data = _read_cache()
    tokens = dict(data.get("tokens") or {})
    tokens[issuerKey(issuer)] = {"idToken": token, "expiresAt": expires_at}
    data["tokens"] = tokens
    _write_cache(data)
    return expires_at


async def clearIdpIdToken(*args: Any, **kwargs: Any) -> None:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    data = _read_cache()
    tokens = dict(data.get("tokens") or {})
    tokens.pop(issuerKey(issuer), None)
    data["tokens"] = tokens
    _write_cache(data)


async def saveIdpClientSecret(*args: Any, **kwargs: Any) -> dict[str, Any]:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    secret = str(kwargs.get("clientSecret") or (args[1] if len(args) > 1 else ""))
    data = _read_cache()
    secrets = dict(data.get("clientSecrets") or {})
    secrets[issuerKey(issuer)] = {"clientSecret": secret}
    data["clientSecrets"] = secrets
    _write_cache(data)
    return {"success": True}


async def getIdpClientSecret(*args: Any, **kwargs: Any) -> str | None:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    entry = (_read_cache().get("clientSecrets") or {}).get(issuerKey(issuer))
    return str(entry.get("clientSecret")) if isinstance(entry, dict) and entry.get("clientSecret") else None


async def clearIdpClientSecret(*args: Any, **kwargs: Any) -> None:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    data = _read_cache()
    secrets = dict(data.get("clientSecrets") or {})
    secrets.pop(issuerKey(issuer), None)
    data["clientSecrets"] = secrets
    _write_cache(data)


async def discoverOidc(*args: Any, **kwargs: Any) -> dict[str, Any]:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    return {
        "issuer": issuer,
        "authorization_endpoint": urljoin(issuer.rstrip("/") + "/", "authorize"),
        "token_endpoint": urljoin(issuer.rstrip("/") + "/", "token"),
        "jwks_uri": urljoin(issuer.rstrip("/") + "/", "jwks"),
    }


async def acquireIdpIdToken(*args: Any, **kwargs: Any) -> dict[str, Any]:
    issuer = str(kwargs.get("idpIssuer") or kwargs.get("issuer") or (args[0] if args else ""))
    cached = await getCachedIdpIdToken(issuer)
    if cached:
        return {"idToken": cached, "cached": True, "issuer": issuer}
    auth_url = urljoin(issuer.rstrip("/") + "/", "authorize") if issuer else ""
    return {
        "idToken": None,
        "cached": False,
        "issuer": issuer,
        "authorizationUrl": auth_url,
        "requiresBrowserLogin": True,
        "reason": "Interactive IdP browser login is disabled in the Python migration shim",
    }


__all__ = [
    "acquireIdpIdToken",
    "clearIdpClientSecret",
    "clearIdpIdToken",
    "discoverOidc",
    "getCachedIdpIdToken",
    "getIdpClientSecret",
    "getXaaIdpSettings",
    "isXaaEnabled",
    "issuerKey",
    "saveIdpClientSecret",
    "saveIdpIdTokenFromJwt",
]
