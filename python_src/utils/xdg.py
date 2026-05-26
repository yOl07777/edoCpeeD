from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _resolve_options(options: dict[str, Any] | None = None) -> tuple[dict[str, str], Path]:
    env = dict(os.environ)
    home = Path.home()
    if options:
        env.update({str(k): str(v) for k, v in (options.get("env") or {}).items() if v is not None})
        if options.get("homedir"):
            home = Path(str(options["homedir"]))
    return env, home


def getXDGStateHome(options: dict[str, Any] | None = None) -> str:
    env, home = _resolve_options(options)
    return env.get("XDG_STATE_HOME") or str(home / ".local" / "state")


def getXDGCacheHome(options: dict[str, Any] | None = None) -> str:
    env, home = _resolve_options(options)
    return env.get("XDG_CACHE_HOME") or str(home / ".cache")


def getXDGDataHome(options: dict[str, Any] | None = None) -> str:
    env, home = _resolve_options(options)
    return env.get("XDG_DATA_HOME") or str(home / ".local" / "share")


def getUserBinDir(options: dict[str, Any] | None = None) -> str:
    _env, home = _resolve_options(options)
    return str(home / ".local" / "bin")
