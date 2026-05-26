from __future__ import annotations

from typing import Any, Iterable


def _command(name: str, description: str, type: str = "local", **extra: Any) -> dict[str, Any]:
    return {
        "name": name,
        "type": type,
        "description": description,
        "source": extra.pop("source", "builtin"),
        **extra,
    }


_BUILTIN_COMMANDS: list[dict[str, Any]] = [
    _command("add-dir", "Add a working directory"),
    _command("agents", "Manage local agents"),
    _command("branch", "Inspect or manage git branches"),
    _command("clear", "Clear the conversation"),
    _command("compact", "Compact conversation context"),
    _command("config", "Read or update configuration"),
    _command("commit", "Create a git commit", "prompt"),
    _command("commit-push-pr", "Commit, push, and open a PR", "prompt"),
    _command("context", "Show current context"),
    _command("cost", "Show current session cost"),
    _command("chrome", "DeepSeek browser-control settings"),
    _command("desktop", "Continue the current session in DeepSeek Desktop"),
    _command("diff", "Show code changes"),
    _command("doctor", "Run local diagnostics"),
    _command("exit", "Exit the session"),
    _command("extra-usage", "Configure DeepSeek extra usage"),
    _command("files", "List tracked files"),
    _command("help", "Show help"),
    _command("hooks", "View DeepSeek hook configurations"),
    _command("ide", "Manage DeepSeek Code IDE integration status"),
    _command("insights", "Generate a report analyzing DeepSeek Code sessions", "prompt"),
    _command("init", "Initialize DeepSeek Code repository guidance files", "prompt"),
    _command("init-verifiers", "Create verifier skills for automated verification", "prompt"),
    _command("install-github-app", "Generate DeepSeek GitHub Actions setup guidance for a repository"),
    _command("install-slack-app", "Show DeepSeek Slack integration setup guidance"),
    _command("memory", "Inspect or update memory"),
    _command("mcp", "Manage local MCP server configuration"),
    _command("mobile", "Show DeepSeek mobile handoff links"),
    _command("model", "Select DeepSeek model"),
    _command("permissions", "Manage permission rules"),
    _command("plan", "Enter or exit plan mode"),
    _command("plugin", "Manage plugins"),
    _command("privacy-settings", "Review and manage privacy settings"),
    _command("rate-limit-options", "Choose what to do after a rate limit"),
    _command("reload-plugins", "Activate pending local plugin metadata changes"),
    _command("remote-env", "Show safe remote environment details"),
    _command("rename", "Rename the current session"),
    _command("resume", "List resumable local sessions"),
    _command("review", "Review code changes", "prompt"),
    _command("rewind", "Rewind the last in-memory session message"),
    _command("sandbox", "Configure local sandbox settings"),
    _command("security-review", "Complete a security review", "prompt"),
    _command("session", "Show session information"),
    _command("share", "Prepare a local share payload"),
    _command("skills", "Manage skills"),
    _command("stats", "Show local session statistics"),
    _command("status", "Show project status"),
    _command("statusline", "Set up DeepSeek Code's status line UI", "prompt"),
    _command("stickers", "Show DeepSeek sticker/community link"),
    _command("summary", "Summarize the current session", "prompt"),
    _command("tag", "Toggle a searchable tag on the current session"),
    _command("tasks", "Manage background tasks"),
    _command("terminal-setup", "Configure terminal key bindings"),
    _command("theme", "Change theme"),
    _command("think-back", "Prepare a DeepSeek Code year-in-review prompt"),
    _command("usage", "Show usage information"),
    _command("web-setup", "Set up DeepSeek Code web handoff and GitHub prerequisites"),
    _command("ultraplan", "Draft an advanced implementation plan"),
    _command("upgrade", "Show DeepSeek account and billing management link"),
    _command("vim", "Toggle vim mode"),
    _command("voice", "Toggle voice mode"),
]

builtInCommandNames = {cmd["name"] for cmd in _BUILTIN_COMMANDS}
INTERNAL_ONLY_COMMANDS: set[str] = {"bridge-kick", "debug-tool-call", "heapdump", "mock-limits", "perf-issue"}
REMOTE_SAFE_COMMANDS: set[str] = {
    "session",
    "exit",
    "clear",
    "help",
    "theme",
    "cost",
    "usage",
    "plan",
    "status",
}
BRIDGE_SAFE_COMMANDS: set[str] = {"compact", "clear", "cost", "summary", "release-notes", "files"}
_commands_cache: dict[str, list[dict[str, Any]]] = {}


def _name_of(cmd: dict[str, Any] | Any) -> str:
    return cmd.get("name", "") if isinstance(cmd, dict) else getattr(cmd, "name", "")


def _aliases_of(cmd: dict[str, Any] | Any) -> list[str]:
    aliases = cmd.get("aliases", []) if isinstance(cmd, dict) else getattr(cmd, "aliases", [])
    return list(aliases or [])


def _enabled(cmd: dict[str, Any] | Any) -> bool:
    if isinstance(cmd, dict):
        checker = cmd.get("isEnabled")
        return bool(checker() if callable(checker) else cmd.get("enabled", True))
    checker = getattr(cmd, "isEnabled", None)
    return bool(checker() if callable(checker) else getattr(cmd, "enabled", True))


def meetsAvailabilityRequirement(cmd: dict[str, Any] | Any) -> bool:
    if isinstance(cmd, dict):
        requirement = cmd.get("availability")
    else:
        requirement = getattr(cmd, "availability", None)
    if requirement in {None, "always", "default"}:
        return True
    if isinstance(requirement, dict):
        return bool(requirement.get("enabled", True))
    if callable(requirement):
        return bool(requirement())
    return bool(requirement)


async def getCommands(cwd: str | None = None) -> list[dict[str, Any]]:
    cache_key = cwd or ""
    if cache_key not in _commands_cache:
        _commands_cache[cache_key] = [
            cmd.copy() for cmd in _BUILTIN_COMMANDS if meetsAvailabilityRequirement(cmd) and _enabled(cmd)
        ]
    return [cmd.copy() for cmd in _commands_cache[cache_key]]


def clearCommandMemoizationCaches() -> None:
    _commands_cache.clear()


def clearCommandsCache() -> None:
    clearCommandMemoizationCaches()


def getMcpSkillCommands(mcpCommands: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        cmd
        for cmd in mcpCommands
        if cmd.get("type") == "prompt" and cmd.get("loadedFrom") == "mcp" and not cmd.get("disableModelInvocation")
    ]


async def getSkillToolCommands(cwd: str | None = None) -> list[dict[str, Any]]:
    return [
        cmd
        for cmd in await getCommands(cwd)
        if cmd.get("type") == "prompt" and not cmd.get("disableModelInvocation") and cmd.get("source") != "builtin"
    ]


async def getSlashCommandToolSkills(cwd: str | None = None) -> list[dict[str, Any]]:
    return await getSkillToolCommands(cwd)


def isBridgeSafeCommand(cmd: dict[str, Any] | Any) -> bool:
    cmd_type = cmd.get("type") if isinstance(cmd, dict) else getattr(cmd, "type", None)
    if cmd_type == "local-jsx":
        return False
    if cmd_type == "prompt":
        return True
    return _name_of(cmd) in BRIDGE_SAFE_COMMANDS


def filterCommandsForRemoteMode(commands: Iterable[dict[str, Any] | Any]) -> list[dict[str, Any] | Any]:
    return [cmd for cmd in commands if _name_of(cmd) in REMOTE_SAFE_COMMANDS]


def findCommand(commandName: str, commands: Iterable[dict[str, Any] | Any]) -> dict[str, Any] | Any | None:
    for cmd in commands:
        if commandName == _name_of(cmd) or commandName in _aliases_of(cmd):
            return cmd
    return None


def hasCommand(commandName: str, commands: Iterable[dict[str, Any] | Any]) -> bool:
    return findCommand(commandName, commands) is not None


def getCommand(commandName: str, commands: Iterable[dict[str, Any] | Any]) -> dict[str, Any] | Any:
    command_list = list(commands)
    command = findCommand(commandName, command_list)
    if command is None:
        available = ", ".join(sorted(_name_of(cmd) for cmd in command_list))
        raise ReferenceError(f"Command {commandName} not found. Available commands: {available}")
    return command


def formatDescriptionWithSource(cmd: dict[str, Any] | Any) -> str:
    getter = cmd.get if isinstance(cmd, dict) else lambda key, default=None: getattr(cmd, key, default)
    description = str(getter("description", ""))
    if getter("type") != "prompt":
        return description
    if getter("kind") == "workflow":
        return f"{description} (workflow)"
    source = getter("source", "builtin")
    if source == "plugin":
        plugin_info = getter("pluginInfo", {}) or {}
        manifest = plugin_info.get("pluginManifest", {}) if isinstance(plugin_info, dict) else {}
        plugin_name = manifest.get("name")
        return f"({plugin_name}) {description}" if plugin_name else f"{description} (plugin)"
    if source in {"builtin", "mcp"}:
        return description
    if source == "bundled":
        return f"{description} (bundled)"
    return f"{description} ({source})"
