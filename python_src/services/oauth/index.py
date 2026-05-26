"""OAuth service wrapper for the Python migration."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Callable

from . import client
from . import crypto

_LISTENER_PATH = Path(__file__).with_name("auth-code-listener.py")
_spec = importlib.util.spec_from_file_location("_deepcode_auth_code_listener", _LISTENER_PATH)
_listener_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules[_spec.name] = _listener_module
_spec.loader.exec_module(_listener_module)
AuthCodeListener = _listener_module.AuthCodeListener


class OAuthService:
    def __init__(self, *, listenerFactory: Callable[[], Any] | None = None) -> None:
        self.codeVerifier = crypto.generateCodeVerifier()
        self.authCodeListener: Any | None = None
        self.port: int | None = None
        self.manualAuthCodeResolver: Callable[[str], None] | None = None
        self.listenerFactory = listenerFactory or AuthCodeListener

    async def startOAuthFlow(
        self,
        authURLHandler: Callable[[str, str | None], Any],
        options: dict[str, Any] | None = None,
        *,
        http_post: Callable[..., Any] | None = None,
        http_get: Callable[..., Any] | None = None,
    ) -> dict[str, Any]:
        options = options or {}
        self.authCodeListener = self.listenerFactory()
        self.port = await self.authCodeListener.start()
        code_challenge = crypto.generateCodeChallenge(self.codeVerifier)
        state = crypto.generateState()
        auth_params = {
            "codeChallenge": code_challenge,
            "state": state,
            "port": self.port,
            "loginWithClaudeAi": options.get("loginWithClaudeAi"),
            "inferenceOnly": options.get("inferenceOnly"),
            "orgUUID": options.get("orgUUID"),
            "loginHint": options.get("loginHint"),
            "loginMethod": options.get("loginMethod"),
        }
        manual_url = client.buildAuthUrl({**auth_params, "isManual": True})
        automatic_url = client.buildAuthUrl({**auth_params, "isManual": False})

        authorization_code = await self.waitForAuthorizationCode(
            state,
            lambda: authURLHandler(manual_url, automatic_url if options.get("skipBrowserOpen") else None),
        )
        is_automatic = bool(self.authCodeListener and self.authCodeListener.hasPendingResponse())
        try:
            token_response = await client.exchangeCodeForTokens(
                authorization_code,
                state,
                self.codeVerifier,
                self.port or 0,
                not is_automatic,
                options.get("expiresIn"),
                http_post=http_post,
            )
            profile_info = await client.fetchProfileInfo(token_response.get("access_token"), http_get=http_get) if http_get else {}
            if is_automatic:
                self.authCodeListener.handleSuccessRedirect(client.parseScopes(token_response.get("scope")))
            return self.formatTokens(
                token_response,
                profile_info.get("subscriptionType"),
                profile_info.get("rateLimitTier"),
                profile_info.get("rawProfile"),
            )
        except Exception:
            if is_automatic and self.authCodeListener:
                self.authCodeListener.handleErrorRedirect()
            raise
        finally:
            self.cleanup()

    async def waitForAuthorizationCode(self, state: str, onReady: Callable[[], Any]) -> str:
        loop = asyncio.get_running_loop()
        manual_future: asyncio.Future[str] = loop.create_future()

        def resolve_manual(code: str) -> None:
            if not manual_future.done():
                manual_future.set_result(code)

        self.manualAuthCodeResolver = resolve_manual
        assert self.authCodeListener is not None
        automatic = asyncio.create_task(self.authCodeListener.waitForAuthorization(state, onReady))
        done, pending = await asyncio.wait({manual_future, automatic}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        self.manualAuthCodeResolver = None
        for task in done:
            if not task.cancelled() and task.exception() is None:
                return task.result()
        first = next(iter(done))
        return first.result()

    def handleManualAuthCodeInput(self, params: dict[str, str]) -> None:
        if self.manualAuthCodeResolver:
            self.manualAuthCodeResolver(params["authorizationCode"])
            self.manualAuthCodeResolver = None
            if self.authCodeListener:
                self.authCodeListener.close()

    def formatTokens(
        self,
        response: dict[str, Any],
        subscriptionType: str | None,
        rateLimitTier: str | None,
        profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "accessToken": response.get("access_token"),
            "refreshToken": response.get("refresh_token"),
            "expiresAt": int(time.time() * 1000) + int(response.get("expires_in") or 3600) * 1000,
            "scopes": client.parseScopes(response.get("scope")),
            "subscriptionType": subscriptionType,
            "rateLimitTier": rateLimitTier,
            "profile": profile,
            "tokenAccount": {
                "uuid": (response.get("account") or {}).get("uuid"),
                "emailAddress": (response.get("account") or {}).get("email_address"),
                "organizationUuid": (response.get("organization") or {}).get("uuid"),
            }
            if response.get("account")
            else None,
        }

    def cleanup(self) -> None:
        if self.authCodeListener:
            self.authCodeListener.close()
        self.manualAuthCodeResolver = None


__all__ = ["AuthCodeListener", "OAuthService"]
