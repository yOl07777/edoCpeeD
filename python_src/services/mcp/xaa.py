"""Cross-App Access (XAA) local shim for migrated MCP auth flows."""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import urljoin, urlparse

TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
JWT_BEARER_GRANT = "urn:ietf:params:oauth:grant-type:jwt-bearer"
ID_JAG_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:id-jag"
ID_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:id_token"


class XaaTokenExchangeError(Exception):
    def __init__(self, message: str, shouldClearIdToken: bool = False) -> None:
        self.shouldClearIdToken = shouldClearIdToken
        super().__init__(message)


def _normalize_url(url: str) -> str:
    try:
        parsed = urlparse(str(url))
        path = parsed.path.rstrip("/")
        netloc = parsed.netloc.lower()
        return parsed._replace(netloc=netloc, path=path).geturl()
    except Exception:
        return str(url).rstrip("/")


async def _json_fetch(fetchFn: Any, url: str, init: dict[str, Any] | None = None) -> Any:
    if fetchFn is None:
        return None
    response = fetchFn(url, init or {})
    if hasattr(response, "__await__"):
        response = await response
    if isinstance(response, dict):
        return response
    json_method = getattr(response, "json", None)
    if callable(json_method):
        data = json_method()
        if hasattr(data, "__await__"):
            data = await data
        return data
    return response


async def discoverProtectedResource(*args: Any, **kwargs: Any) -> dict[str, Any]:
    serverUrl = str(kwargs.get("serverUrl") or (args[0] if args else ""))
    fetchFn = kwargs.get("fetchFn") or (kwargs.get("opts") or {}).get("fetchFn")
    metadata = await _json_fetch(fetchFn, urljoin(serverUrl.rstrip("/") + "/", ".well-known/oauth-protected-resource"))
    if not isinstance(metadata, dict):
        metadata = {"resource": serverUrl, "authorization_servers": []}
    metadata.setdefault("resource", serverUrl)
    metadata.setdefault("authorization_servers", [])
    if _normalize_url(metadata["resource"]) != _normalize_url(serverUrl):
        raise ValueError(f"XAA: PRM resource mismatch: expected {serverUrl}, got {metadata['resource']}")
    return {
        "resource": metadata["resource"],
        "authorization_servers": list(metadata.get("authorization_servers") or []),
    }


async def discoverAuthorizationServer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    asUrl = str(kwargs.get("asUrl") or (args[0] if args else ""))
    fetchFn = kwargs.get("fetchFn") or (kwargs.get("opts") or {}).get("fetchFn")
    metadata = await _json_fetch(fetchFn, urljoin(asUrl.rstrip("/") + "/", ".well-known/oauth-authorization-server"))
    if not isinstance(metadata, dict):
        metadata = {"issuer": asUrl, "token_endpoint": urljoin(asUrl.rstrip("/") + "/", "token")}
    metadata.setdefault("issuer", asUrl)
    metadata.setdefault("token_endpoint", urljoin(asUrl.rstrip("/") + "/", "token"))
    if _normalize_url(metadata["issuer"]) != _normalize_url(asUrl):
        raise ValueError(f"XAA: AS issuer mismatch: expected {asUrl}, got {metadata['issuer']}")
    if urlparse(str(metadata["token_endpoint"])).scheme not in {"https", "http"}:
        raise ValueError(f"XAA: invalid token endpoint: {metadata['token_endpoint']}")
    return {
        "issuer": metadata["issuer"],
        "token_endpoint": metadata["token_endpoint"],
        "grant_types_supported": metadata.get("grant_types_supported", []),
        "token_endpoint_auth_methods_supported": metadata.get("token_endpoint_auth_methods_supported", []),
    }


def _fake_token(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return prefix + "." + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


async def requestJwtAuthorizationGrant(*args: Any, **kwargs: Any) -> dict[str, Any]:
    idToken = str(kwargs.get("idToken") or kwargs.get("subjectToken") or (args[0] if args else ""))
    if not idToken:
        raise XaaTokenExchangeError("XAA: missing IdP id_token", True)
    return {
        "jwtAuthGrant": _fake_token("id-jag", {"subject_token": idToken[:12], "grant_type": TOKEN_EXCHANGE_GRANT}),
        "expiresIn": 3600,
        "scope": kwargs.get("scope"),
    }


async def exchangeJwtAuthGrant(*args: Any, **kwargs: Any) -> dict[str, Any]:
    grant = str(kwargs.get("jwtAuthGrant") or kwargs.get("assertion") or (args[0] if args else ""))
    if not grant:
        raise XaaTokenExchangeError("XAA: missing JWT authorization grant", False)
    return {
        "access_token": _fake_token("mcp-access", {"assertion": grant[:16], "grant_type": JWT_BEARER_GRANT}),
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": kwargs.get("scope"),
    }


async def performCrossAppAccess(*args: Any, **kwargs: Any) -> dict[str, Any]:
    serverUrl = str(kwargs.get("serverUrl") or (args[0] if args else ""))
    idToken = str(kwargs.get("idToken") or kwargs.get("subjectToken") or (args[1] if len(args) > 1 else ""))
    prm = await discoverProtectedResource(serverUrl)
    as_url = kwargs.get("authorizationServer") or (prm["authorization_servers"][0] if prm["authorization_servers"] else serverUrl)
    as_meta = await discoverAuthorizationServer(as_url)
    grant = await requestJwtAuthorizationGrant(idToken=idToken, scope=kwargs.get("scope"))
    token = await exchangeJwtAuthGrant(jwtAuthGrant=grant["jwtAuthGrant"], scope=kwargs.get("scope"))
    return {"protectedResource": prm, "authorizationServer": as_meta, "jwtAuthGrant": grant, "token": token}


__all__ = [
    "XaaTokenExchangeError",
    "discoverAuthorizationServer",
    "discoverProtectedResource",
    "exchangeJwtAuthGrant",
    "performCrossAppAccess",
    "requestJwtAuthorizationGrant",
]
