from __future__ import annotations

import fnmatch
import re
import shlex
from dataclasses import dataclass
from typing import Any

from python_src.tools.BashTool.bashSecurity import bashCommandIsSafe_DEPRECATED
from python_src.tools.BashTool.destructiveCommandWarning import getDestructiveCommandWarning
from python_src.tools.BashTool.readOnlyValidation import isCommandSafeViaFlagParsing


BINARY_HIJACK_VARS = {"PATH", "PYTHONPATH", "NODE_PATH", "LD_PRELOAD", "DYLD_INSERT_LIBRARIES"}
MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 8
MAX_SUGGESTED_RULES_FOR_COMPOUND = 4


@dataclass(frozen=True)
class BashPermissionRule:
    pattern: str
    read_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"pattern": self.pattern, "read_only": self.read_only}


bashPermissionRule = BashPermissionRule


def _argv(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return []


def stripAllLeadingEnvVars(command: str) -> str:
    argv = _argv(command)
    while argv and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0]):
        argv.pop(0)
    return " ".join(shlex.quote(arg) for arg in argv) if argv else command.strip()


def stripWrappersFromArgv(argv: list[str]) -> list[str]:
    wrappers = {"env", "command", "builtin", "time", "noglob"}
    cleaned = list(argv)
    while cleaned and cleaned[0] in wrappers:
        cleaned.pop(0)
        while cleaned and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", cleaned[0]):
            cleaned.pop(0)
    return cleaned


def stripSafeWrappers(command: str) -> str:
    argv = stripWrappersFromArgv(_argv(stripAllLeadingEnvVars(command)))
    return " ".join(shlex.quote(arg) for arg in argv) if argv else command.strip()


def getFirstWordPrefix(command: str) -> str:
    cleaned = stripSafeWrappers(command)
    argv = _argv(cleaned)
    return argv[0] if argv else ""


def getSimpleCommandPrefix(command: str) -> str:
    cleaned = stripSafeWrappers(command)
    argv = _argv(cleaned)
    if not argv:
        return ""
    if argv[0] == "git" and len(argv) > 1:
        return f"git {argv[1]}"
    return argv[0]


def permissionRuleExtractPrefix(rule: str | dict[str, Any] | BashPermissionRule) -> str:
    if isinstance(rule, BashPermissionRule):
        return rule.pattern
    if isinstance(rule, dict):
        return str(rule.get("pattern") or rule.get("prefix") or "")
    return str(rule)


def matchWildcardPattern(pattern: str, value: str) -> bool:
    return fnmatch.fnmatchcase(value, pattern)


def bashToolCheckExactMatchPermission(command: str, rules: list[str | dict[str, Any] | BashPermissionRule]) -> bool:
    normalized = stripSafeWrappers(command)
    return any(normalized == permissionRuleExtractPrefix(rule) for rule in rules)


def bashToolCheckPermission(command: str, rules: list[str | dict[str, Any] | BashPermissionRule]) -> bool:
    normalized = stripSafeWrappers(command)
    prefix = getSimpleCommandPrefix(normalized)
    for rule in rules:
        pattern = permissionRuleExtractPrefix(rule)
        if not pattern:
            continue
        if pattern.endswith("*") and matchWildcardPattern(pattern, normalized):
            return True
        if normalized == pattern or normalized.startswith(pattern + " ") or prefix == pattern:
            return True
    return False


def isNormalizedCdCommand(command: str) -> bool:
    return getFirstWordPrefix(command) in {"cd", "pushd", "popd"}


def isNormalizedGitCommand(command: str) -> bool:
    return getFirstWordPrefix(command) == "git"


def commandHasAnyCd(command: str) -> bool:
    return any(isNormalizedCdCommand(part.strip()) for part in re.split(r";|&&|\|\|", command))


def checkCommandAndSuggestRules(command: str) -> dict[str, Any]:
    warning = getDestructiveCommandWarning(command)
    read_only = isCommandSafeViaFlagParsing(command)
    safe = bashCommandIsSafe_DEPRECATED(command)
    suggestions: list[dict[str, Any]] = []
    prefix = getSimpleCommandPrefix(command)
    if prefix and safe:
        suggestions.append(BashPermissionRule(prefix, read_only=read_only).to_dict())
    return {
        "allowed": read_only,
        "safe": safe,
        "warning": warning,
        "suggested_rules": suggestions[:MAX_SUGGESTED_RULES_FOR_COMPOUND],
    }


async def bashToolHasPermission(
    command: str,
    *,
    rules: list[str | dict[str, Any] | BashPermissionRule] | None = None,
    read_only_mode: bool = False,
) -> dict[str, Any]:
    if read_only_mode:
        ok = isCommandSafeViaFlagParsing(command)
        return {"allowed": ok, "reason": None if ok else "Command is not read-only."}
    if bashToolCheckPermission(command, rules or []):
        return {"allowed": True, "reason": None}
    check = checkCommandAndSuggestRules(command)
    return {"allowed": bool(check["allowed"]), "reason": check.get("warning"), "suggested_rules": check["suggested_rules"]}


_SPECULATIVE: dict[str, dict[str, Any]] = {}


async def executeAsyncClassifierCheck(command: str, **_: Any) -> dict[str, Any]:
    return checkCommandAndSuggestRules(command)


async def awaitClassifierAutoApproval(command: str, **kwargs: Any) -> dict[str, Any]:
    return await executeAsyncClassifierCheck(command, **kwargs)


async def startSpeculativeClassifierCheck(command: str, **kwargs: Any) -> dict[str, Any]:
    result = await executeAsyncClassifierCheck(command, **kwargs)
    _SPECULATIVE[command] = result
    return result


async def peekSpeculativeClassifierCheck(command: str) -> dict[str, Any] | None:
    return _SPECULATIVE.get(command)


async def consumeSpeculativeClassifierCheck(command: str) -> dict[str, Any] | None:
    return _SPECULATIVE.pop(command, None)


async def clearSpeculativeChecks() -> None:
    _SPECULATIVE.clear()
