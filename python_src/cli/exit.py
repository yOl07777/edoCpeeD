"""CLI exit helpers for subcommand handlers."""

from __future__ import annotations

import sys


class CLIExit(SystemExit):
    """SystemExit carrying the user-facing message written by the helper."""

    def __init__(self, code: int, message: str | None = None) -> None:
        super().__init__(code)
        self.message = message


def cliError(msg: str | None = None) -> None:
    if msg:
        print(msg, file=sys.stderr)
    raise CLIExit(1, msg)


def cliOk(msg: str | None = None) -> None:
    if msg:
        sys.stdout.write(msg + "\n")
    raise CLIExit(0, msg)
