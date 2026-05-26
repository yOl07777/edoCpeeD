"""Shared bridge protocol constants and lightweight Python data shapes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Mapping, Protocol

DEFAULT_SESSION_TIMEOUT_MS = 24 * 60 * 60 * 1000
BRIDGE_LOGIN_INSTRUCTION = (
    "Remote Control is only available with claude.ai subscriptions. "
    "Please use `/login` to sign in with your claude.ai account."
)
BRIDGE_LOGIN_ERROR = (
    "Error: You must be logged in to use Remote Control.\n\n"
    + BRIDGE_LOGIN_INSTRUCTION
)
REMOTE_CONTROL_DISCONNECTED_MSG = "Remote Control disconnected."

SessionDoneStatus = Literal["completed", "failed", "interrupted"]
SessionActivityType = Literal["tool_start", "text", "result", "error"]
SpawnMode = Literal["single-session", "worktree", "same-dir"]
BridgeWorkerType = Literal["claude_code", "claude_code_assistant", "deepseek_code"]


@dataclass(slots=True)
class WorkData:
    type: Literal["session", "healthcheck"]
    id: str


@dataclass(slots=True)
class WorkResponse:
    id: str
    type: str
    environment_id: str
    state: str
    data: WorkData | dict[str, Any]
    secret: str
    created_at: str


@dataclass(slots=True)
class WorkSecret:
    version: int
    session_ingress_token: str
    api_base_url: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    auth: list[dict[str, str]] = field(default_factory=list)
    claude_code_args: Mapping[str, str] | None = None
    mcp_config: Any | None = None
    environment_variables: Mapping[str, str] | None = None
    use_code_sessions: bool | None = None


@dataclass(slots=True)
class SessionActivity:
    type: SessionActivityType
    summary: str
    timestamp: float


class BridgeLogger(Protocol):
    def debug(self, message: str, *args: Any) -> None: ...
    def info(self, message: str, *args: Any) -> None: ...
    def warn(self, message: str, *args: Any) -> None: ...
    def error(self, message: str, *args: Any) -> None: ...


class SessionHandle(Protocol):
    sessionId: str
    title: str | None

    async def stop(self) -> None: ...


SessionSpawner = Callable[..., Any]
