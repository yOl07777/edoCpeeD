from __future__ import annotations

import shlex
from dataclasses import dataclass


READ_ONLY_COMMANDS = {
    "awk",
    "cat",
    "cut",
    "diff",
    "dir",
    "du",
    "echo",
    "find",
    "git",
    "grep",
    "head",
    "jq",
    "less",
    "ls",
    "pwd",
    "rg",
    "sed",
    "sort",
    "stat",
    "tail",
    "tree",
    "tr",
    "type",
    "uniq",
    "wc",
    "which",
}
MUTATING_GIT_SUBCOMMANDS = {
    "add",
    "am",
    "apply",
    "bisect",
    "branch",
    "checkout",
    "cherry-pick",
    "clean",
    "commit",
    "merge",
    "mv",
    "pull",
    "push",
    "rebase",
    "reset",
    "restore",
    "revert",
    "rm",
    "stash",
    "switch",
    "tag",
}
SHELL_WRITE_OPERATORS = {">", ">>", ">|"}


@dataclass(frozen=True)
class ReadOnlyValidation:
    ok: bool
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "reason": self.reason}


def _split_statements(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    parts: list[list[str]] = [[]]
    for token in lexer:
        if token in {";", "&&", "||", "|"}:
            if parts[-1]:
                parts.append([])
            continue
        parts[-1].append(token)
    return [part for part in parts if part]


def isCommandSafeViaFlagParsing(command: str) -> bool:
    try:
        statements = _split_statements(command)
    except ValueError:
        return False
    if not statements:
        return False

    for argv in statements:
        if any(token in SHELL_WRITE_OPERATORS for token in argv):
            return False
        exe = argv[0].lower()
        if exe not in READ_ONLY_COMMANDS:
            return False
        if exe == "git":
            subcommand = next((arg.lower() for arg in argv[1:] if not arg.startswith("-")), "")
            if subcommand in MUTATING_GIT_SUBCOMMANDS:
                return False
        if exe == "sed" and any(arg in {"-i", "--in-place"} or arg.startswith("-i") for arg in argv[1:]):
            return False
        if exe == "find" and any(arg in {"-delete", "-exec", "-execdir"} for arg in argv[1:]):
            return False
    return True


def checkReadOnlyConstraints(command: str) -> dict[str, object]:
    ok = isCommandSafeViaFlagParsing(command)
    reason = None if ok else "Command is not provably read-only."
    return ReadOnlyValidation(ok=ok, reason=reason).to_dict()
