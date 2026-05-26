"""Bridge command-line entry points for the Python migration."""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from dataclasses import dataclass, field
from typing import Any, Sequence
from uuid import uuid4

from .bridgeUI import createBridgeLogger
from .initReplBridge import initReplBridge


class BridgeHeadlessPermanentError(Exception):
    """Non-retryable bridge startup failure."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass
class BridgeState:
    environmentId: str
    connected: bool = False
    reconnecting: bool = False
    activeSessions: dict[str, Any] = field(default_factory=dict)
    startedAt: float = field(default_factory=time.time)
    lastError: str | None = None


def _status_of(error: Any) -> int | None:
    for attr in ("status", "status_code", "code"):
        value = getattr(error, attr, None)
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        return number
    response = getattr(error, "response", None)
    if response is not None:
        return _status_of(response)
    return None


def isConnectionError(error: Any) -> bool:
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return True
    text = str(error).lower()
    return any(
        marker in text
        for marker in (
            "econnreset",
            "econnrefused",
            "enotfound",
            "network",
            "timeout",
            "connection",
            "dns",
            "fetch failed",
        )
    )


def isServerError(error: Any) -> bool:
    status = _status_of(error)
    if status is not None:
        return 500 <= status <= 599
    text = str(error).lower()
    return "server error" in text or "5xx" in text or "status 500" in text


def parseArgs(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="deepseek-code bridge", add_help=True)
    parser.add_argument("directory", nargs="?", default=os.getcwd())
    parser.add_argument("--session-id", dest="session_id")
    parser.add_argument("--continue", dest="continue_session", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--spawn", dest="spawn_mode", choices=["single-session", "worktree", "same-dir"])
    parser.add_argument("--max-sessions", type=int, default=32)
    parser.add_argument("--sdk-url", dest="sdk_url")
    parser.add_argument("--access-token", dest="access_token")
    parser.add_argument("--envless", action="store_true")
    return parser.parse_args(list(argv) if argv is not None else None)


async def runBridgeHeadless(options: dict[str, Any] | argparse.Namespace | None = None, **kwargs: Any) -> dict[str, Any]:
    opts = vars(options) if isinstance(options, argparse.Namespace) else dict(options or {})
    opts.update(kwargs)
    logger = opts.get("logger") or createBridgeLogger({"quiet": opts.get("quiet", True), "verbose": opts.get("verbose", False)})
    session_id = str(opts.get("session_id") or opts.get("sessionId") or f"session_{uuid4().hex}")
    handle = await initReplBridge(
        {
            "sessionId": session_id,
            "sdkUrl": opts.get("sdk_url") or opts.get("sdkUrl") or "memory://bridge",
            "accessToken": opts.get("access_token") or opts.get("accessToken"),
            "envless": bool(opts.get("envless", True)),
            "outboundOnly": opts.get("outboundOnly", False),
        }
    )
    logger.info(f"Bridge headless session ready: {session_id}")
    return {"mode": "headless", "sessionId": session_id, "handle": handle, "logger": logger}


async def runBridgeLoop(
    config: dict[str, Any] | None = None,
    *_args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    opts = {**(config or {}), **kwargs}
    environment_id = str(opts.get("environmentId") or opts.get("environment_id") or f"env_{uuid4().hex}")
    logger = opts.get("logger") or createBridgeLogger({"quiet": opts.get("quiet", True), "verbose": opts.get("verbose", False)})
    state = BridgeState(environmentId=environment_id, connected=True)
    logger.updateIdleStatus(environmentId=environment_id)
    if opts.get("initialSessionId"):
        state.activeSessions[str(opts["initialSessionId"])] = await initReplBridge(
            {
                "sessionId": str(opts["initialSessionId"]),
                "sdkUrl": opts.get("sdkUrl") or "memory://bridge",
                "accessToken": opts.get("accessToken"),
                "envless": bool(opts.get("envless", True)),
            }
        )
    return {"running": True, "state": state, "logger": logger}


async def bridgeMain(argv: Sequence[str] | None = None) -> dict[str, Any]:
    args = parseArgs(argv)
    if args.headless:
        return await runBridgeHeadless(args)
    return await runBridgeLoop(
        {
            "directory": args.directory,
            "sdkUrl": args.sdk_url,
            "accessToken": args.access_token,
            "quiet": args.quiet,
            "verbose": args.verbose,
            "envless": args.envless,
            "initialSessionId": args.session_id if args.continue_session else None,
            "maxSessions": args.max_sessions,
            "spawnMode": args.spawn_mode or "single-session",
        }
    )


def main() -> None:
    asyncio.run(bridgeMain())


if __name__ == "__main__":
    main()
