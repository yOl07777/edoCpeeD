import asyncio
import importlib
from pathlib import Path

import pytest

from deepseek_code.core.types import InternalToolCall
from python_src.commands.clear.conversation import clearConversation
from python_src.commands.cost.cost import cost_command
from python_src.commands.memory.memory import memory_command
from python_src.commands.session.session import session_command
from python_src.cost_store import COST_STATE
from python_src.session_store import SESSION_STATE
from python_src.tools import build_default_tool_registry, get_deepseek_tools
from python_src.tools.AgentTool.AgentTool import agent
from python_src.tools.AskUserQuestionTool.AskUserQuestionTool import ask_user_question
from python_src.tools.BashTool.BashTool import detectBlockedSleepPattern, isSearchOrReadBashCommand
from python_src.tools.BashTool.bashPermissions import bashToolHasPermission, getSimpleCommandPrefix
from python_src.tools.BashTool.destructiveCommandWarning import getDestructiveCommandWarning
from python_src.tools.BashTool.modeValidation import checkPermissionMode
from python_src.tools.BashTool.pathValidation import checkPathConstraints
from python_src.tools.BashTool.readOnlyValidation import isCommandSafeViaFlagParsing
from python_src.tools.ConfigTool.ConfigTool import config_tool
from python_src.tools.EnterPlanModeTool.EnterPlanModeTool import enter_plan_mode
from python_src.tools.ExitPlanModeTool.ExitPlanModeV2Tool import exit_plan_mode
from python_src.tools.FileEditTool.FileEditTool import edit_file
from python_src.tools.FileReadTool.FileReadTool import read_file
from python_src.tools.FileWriteTool.FileWriteTool import write_file
from python_src.tools.GlobTool.GlobTool import glob_files
from python_src.tools.GrepTool.GrepTool import grep_files
from python_src.tools.ListMcpResourcesTool.ListMcpResourcesTool import list_mcp_resources
from python_src.tools.LSPTool.LSPTool import lsp_symbol_search
from python_src.tools.NotebookEditTool.NotebookEditTool import notebook_edit
from python_src.tools.PowerShellTool.PowerShellTool import detectBlockedSleepPattern as ps_blocked_sleep
from python_src.tools.PowerShellTool.modeValidation import checkPermissionMode as ps_check_permission_mode
from python_src.tools.PowerShellTool.pathValidation import checkPathConstraints as ps_check_path_constraints
from python_src.tools.PowerShellTool.powershellPermissions import powershellToolHasPermission
from python_src.tools.PowerShellTool.powershellSecurity import powershellCommandIsSafe
from python_src.tools.PowerShellTool.readOnlyValidation import isReadOnlyCommand
from python_src.tools.ReadMcpResourceTool.ReadMcpResourceTool import read_mcp_resource
from python_src.tools.RemoteTriggerTool.RemoteTriggerTool import remote_trigger
from python_src.tools.ScheduleCronTool.CronCreateTool import cron_create
from python_src.tools.ScheduleCronTool.CronDeleteTool import cron_delete
from python_src.tools.ScheduleCronTool.CronListTool import cron_list
from python_src.tools.SkillTool.SkillTool import skill
from python_src.tools.SleepTool.SleepTool import sleep_tool
from python_src.tools.MonitorTool.MonitorTool import monitor
from python_src.tools.WorkflowTool.WorkflowTool import workflow
from python_src.tools.shared.gitOperationTracking import detectGitOperation, parseGitCommitId, trackGitOperations
from python_src.tools.TaskCreateTool.TaskCreateTool import task_create
from python_src.tools.TaskGetTool.TaskGetTool import task_get
from python_src.tools.TaskListTool.TaskListTool import task_list
from python_src.tools.TaskOutputTool.TaskOutputTool import task_output
from python_src.tools.TaskStopTool.TaskStopTool import task_stop
from python_src.tools.TaskUpdateTool.TaskUpdateTool import task_update
from python_src.tools.TeamCreateTool.TeamCreateTool import team_create
from python_src.tools.TeamDeleteTool.TeamDeleteTool import team_delete
from python_src.tools.TodoWriteTool.TodoWriteTool import todo_write
from python_src.tools.SendMessageTool.SendMessageTool import send_agent_message
from python_src.tools.agent_store import clear_agent_state
from python_src.tools.mcp_resource_store import RESOURCES, register_resource
from python_src.tools.path_utils import resolve_workspace_path
from python_src.tools.schedule_store import clear_schedule_state
from python_src.tools.task_store import clear_tasks
from python_src.commands.permissions.index import permissions_command
from python_src.commands.diff.index import diff_command
from python_src.commands.branch.branch import call as branch_call, deriveFirstPrompt
from python_src.commands.issue.index import issue_command
from python_src.commands.config.index import config_command
from python_src.commands.model.index import model_command
from python_src.commands.pr_comments.index import pr_comments_command
from python_src.commands.review.reviewRemote import checkOverageGate, launchRemoteReview
from python_src.commands.status.index import status_command
from python_src.hooks.toolPermission.PermissionContext import createPermissionContext
from python_src.hooks.toolPermission.handlers.interactiveHandler import handleInteractivePermission
from python_src.hooks.toolPermission.permissionLogging import clearPermissionLog, getPermissionLog
from python_src.utils.permissions.PermissionMode import (
    getModeColor,
    permissionModeFromString,
    permissionModeShortTitle,
)
from python_src.utils.permissions.PermissionResult import getRuleBehaviorDescription
from python_src.utils.permissions.PermissionUpdate import createReadRuleSuggestion, persistPermissionUpdate
from python_src.utils.permissions.autoModeState import (
    _resetForTesting,
    isAutoModeActive,
    setAutoModeActive,
    setAutoModeCircuitBroken,
)
from python_src.utils.permissions.filesystem import (
    checkReadPermissionForTool,
    checkWritePermissionForTool,
    getSessionMemoryPath,
    pathInWorkingPath,
)
from python_src.utils.permissions.permissionRuleParser import (
    permissionRuleValueFromString,
    permissionRuleValueToString,
)
from python_src.utils.permissions.permissions import checkRuleBasedPermissions
from python_src.utils.permissions.permissionsLoader import loadAllPermissionRulesFromDisk
from python_src.utils.git.gitConfigParser import parseConfigString, parseGitConfigValue
from python_src.utils.git.gitFilesystem import (
    clearResolveGitDirCache,
    getCachedBranch,
    getCachedDefaultBranch,
    getCachedHead,
    getCachedRemoteUrl,
    getWorktreeCountFromFs,
    isSafeRefName,
    isValidGitSha,
    resolveGitDir,
)
from python_src.utils.git.gitignore import addFileGlobRuleToGitignore, isPathGitignored
from python_src.utils.github.ghAuthStatus import getGhAuthStatus
from python_src.utils.settings.settings import (
    getInitialSettings,
    getSettingsFilePathForSource,
    getSettingsWithSources,
    hasAutoModeOptIn,
    parseSettingsFile,
    rawSettingsContainsKey,
)
from python_src.utils.settings.settingsCache import resetSettingsCache
from python_src.utils.settings.types import isMcpServerCommandEntry, isMcpServerUrlEntry
from python_src.utils.settings.validation import validateSettingsFileContent
from python_src.utils.model.agent import getAgentModel, getAgentModelDisplay, getAgentModelOptions
from python_src.utils.model.aliases import isModelAlias, isModelFamilyAlias
from python_src.utils.model.deprecation import getModelDeprecationWarning
from python_src.utils.model.model import (
    getBestModel,
    getCanonicalName,
    getDefaultMainLoopModel,
    getDefaultOpusModel,
    getMarketingNameForModel,
    normalizeModelStringForAPI,
    resolveSkillModelOverride,
)
from python_src.utils.model.modelAllowlist import isModelAllowed
from python_src.utils.model.modelCapabilities import getModelCapability, refreshModelCapabilities
from python_src.utils.model.modelOptions import getDefaultOptionForUser, getModelOptions
from python_src.utils.model.modelStrings import getModelStrings, resolveOverriddenModel
from python_src.utils.model.providers import getAPIProvider, isFirstPartyAnthropicBaseUrl
from python_src.utils.model.validateModel import validateModel
from python_src.commands.compact.index import compact_command
from python_src.commands.context.context import call as context_command
from python_src.services.compact.compact import (
    compactConversation,
    createPostCompactFileAttachments,
    stripImagesFromMessages,
    truncateHeadForPTLRetry,
)
from python_src.services.compact.compactWarningState import (
    clearCompactWarningSuppression,
    suppressCompactWarning,
)
from python_src.services.compact.grouping import groupMessagesByApiRound
from python_src.services.compact.prompt import getCompactPrompt, getCompactUserSummaryMessage
from python_src.utils.messages.mappers import (
    localCommandOutputToSDKAssistantMessage,
    toInternalMessages,
    toSDKCompactMetadata,
    toSDKMessages,
)
from python_src.utils.messages.systemInit import buildSystemInitMessage, sdkCompatToolName


def test_tool_schemas_are_deepseek_function_tools():
    schemas = get_deepseek_tools()

    assert {schema["function"]["name"] for schema in schemas} >= {
        "read_file",
        "write_file",
        "glob_files",
        "grep_files",
        "run_shell",
        "run_powershell",
        "config",
        "notebook_edit",
        "list_mcp_resources",
        "read_mcp_resource",
        "skill",
        "enter_plan_mode",
        "exit_plan_mode",
        "lsp_symbol_search",
        "memory",
        "session",
        "cost",
        "clear_conversation",
        "agent",
        "sleep",
        "cron_create",
        "cron_list",
        "cron_delete",
        "monitor",
        "remote_trigger",
        "plugin",
        "reload_plugins",
        "output_style",
        "workflow",
        "team_create",
        "team_delete",
        "send_message",
        "ask_user_question",
        "edit_file",
        "todo_write",
        "task_create",
        "task_get",
        "task_list",
        "task_update",
        "task_stop",
        "task_output",
        "web_fetch",
        "web_search",
    }
    assert all(schema["type"] == "function" for schema in schemas)


def test_file_tools_glob_and_grep(tmp_path: Path):
    async def run() -> None:
        await write_file("a.txt", "alpha\nbeta\n", cwd=str(tmp_path))
        read = await read_file("a.txt", cwd=str(tmp_path), limit=1)
        globbed = await glob_files("*.txt", cwd=str(tmp_path))
        grepped = await grep_files("beta", cwd=str(tmp_path), include="*.txt")

        assert read["content"] == "alpha"
        assert len(globbed["matches"]) == 1
        assert grepped["matches"][0]["line"] == 2

    asyncio.run(run())


def test_edit_todo_and_task_tools(tmp_path: Path):
    async def run() -> None:
        clear_tasks()
        await write_file("note.txt", "alpha beta", cwd=str(tmp_path))
        edit = await edit_file("note.txt", "beta", "gamma", cwd=str(tmp_path))
        todos = await todo_write(
            [{"content": "finish migration", "status": "in_progress"}],
            cwd=str(tmp_path),
        )
        task = await task_create("Continue migration", description="Move more tools")
        updated = await task_update(task["id"], status="in_progress")
        with_output = await task_output(task["id"], "started")
        fetched = await task_get(task["id"])
        listed = await task_list(status="in_progress")
        stopped = await task_stop(task["id"], reason="done")

        assert edit["replacements"] == 1
        assert (tmp_path / "note.txt").read_text(encoding="utf-8") == "alpha gamma"
        assert todos["count"] == 1
        assert task["id"].startswith("task_")
        assert updated["status"] == "in_progress"
        assert with_output["output"] == ["started"]
        assert fetched["title"] == "Continue migration"
        assert listed["count"] == 1
        assert stopped["status"] == "stopped"

    asyncio.run(run())


def test_config_notebook_and_mcp_tools(tmp_path: Path):
    async def run() -> None:
        RESOURCES.clear()
        await config_tool("set", key="model", value="deepseek-chat", cwd=str(tmp_path))
        config = await config_tool("get", key="model", cwd=str(tmp_path))
        notebook_path = tmp_path / "demo.ipynb"
        notebook_path.write_text(
            '{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}',
            encoding="utf-8",
        )
        notebook = await notebook_edit("demo.ipynb", 0, "print('hi')\n", cwd=str(tmp_path))
        register_resource("memory://note", "hello", name="note")
        listed = await list_mcp_resources()
        resource = await read_mcp_resource("memory://note")

        assert config["value"] == "deepseek-chat"
        assert notebook["cell_count"] == 1
        assert listed["count"] == 1
        assert resource["content"] == "hello"

    asyncio.run(run())


def test_skill_plan_lsp_and_git_helpers(tmp_path: Path):
    async def run() -> None:
        skill_dir = tmp_path / ".codex" / "skills" / "demo"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Demo\nUse this skill.", encoding="utf-8")
        (tmp_path / "sample.py").write_text("class Alpha:\n    pass\n\ndef beta():\n    pass\n", encoding="utf-8")

        skills = await skill("list", cwd=str(tmp_path))
        read_skill = await skill("read", name="demo", cwd=str(tmp_path))
        plan = await enter_plan_mode("Migrate", [{"step": "test", "status": "pending"}])
        exited = await exit_plan_mode()
        symbols = await lsp_symbol_search("Alpha", cwd=str(tmp_path), include="*.py")

        assert skills["skills"][0]["name"] == "demo"
        assert "Demo" in read_skill["content"]
        assert plan["active"] is True
        assert exited["active"] is False
        assert symbols["results"][0]["symbol"] == "Alpha"

    asyncio.run(run())

    assert detectGitOperation("git commit -m hi") == {"is_git": True, "operation": "commit"}
    assert parseGitCommitId("commit abc1234") == "abc1234"
    assert trackGitOperations("git rev-parse HEAD", "abc1234")["commit_id"] == "abc1234"


def test_memory_session_cost_and_clear_commands(tmp_path: Path):
    async def run() -> None:
        SESSION_STATE.clear()
        COST_STATE.reset()
        memory = await memory_command("append", content="Remember this.", cwd=str(tmp_path))
        prompt = await memory_command("prompt", cwd=str(tmp_path))
        added = await session_command("add", role="user", content="hello")
        listed = await session_command("list")
        cost = await cost_command("add", input_tokens=3, output_tokens=4, total_usd=0.01)
        cleared = clearConversation()

        assert memory["appended"] == "Remember this."
        assert "Remember this." in prompt["prompt"]
        assert added["message"]["content"] == "hello"
        assert listed["count"] == 1
        assert cost["total_tokens"] == 7
        assert cleared["cleared"] == 1

    asyncio.run(run())


def test_agent_team_message_and_question_tools():
    async def run() -> None:
        clear_agent_state()
        created = await agent("create", name="worker", prompt="Help with code")
        listed = await agent("list")
        team = await team_create("devs", [created["id"]])
        message = await send_agent_message(team["id"], "hello team")
        fetched = await agent("get", agent_id=created["id"])
        question = await ask_user_question("ask", question="Proceed?", choices=["yes", "no"])
        answered = await ask_user_question("answer", question_id=question["id"], answer="yes")
        deleted = await team_delete(team["id"])

        assert listed["count"] == 1
        assert message["content"] == "hello team"
        assert fetched["messages"][0]["content"] == "hello team"
        assert answered["answer"] == "yes"
        assert deleted["id"] == team["id"]

    asyncio.run(run())


def test_schedule_monitor_sleep_and_trigger_tools():
    async def run() -> None:
        clear_schedule_state()
        slept = await sleep_tool(0)
        cron = await cron_create("daily", "say hi", "daily")
        crons = await cron_list()
        deleted = await cron_delete(cron["id"])
        created_monitor = await monitor(
            "create",
            name="watch",
            target="README.md",
            condition="changes",
        )
        monitors = await monitor("list")
        trigger = await remote_trigger("deploy", {"branch": "main"})

        assert slept["slept_seconds"] == 0
        assert crons["count"] == 1
        assert deleted["status"] == "deleted"
        assert monitors["monitors"][0]["id"] == created_monitor["id"]
        assert trigger["payload"]["branch"] == "main"

    asyncio.run(run())


def test_plugin_output_style_and_workflow_tools(tmp_path: Path):
    async def run() -> None:
        plugin_command = importlib.import_module("python_src.commands.plugin.plugin").plugin_command
        reload_plugins = importlib.import_module("python_src.commands.reload-plugins.reload-plugins").reload_plugins
        output_style = importlib.import_module("python_src.commands.output-style.output-style").output_style

        manifest = tmp_path / "demo" / ".codex-plugin"
        manifest.mkdir(parents=True)
        (manifest / "plugin.json").write_text('{"name":"demo","version":"1.0.0"}', encoding="utf-8")
        style_dir = tmp_path / ".deepseek_output_styles"
        style_dir.mkdir()
        (style_dir / "brief.md").write_text("Be brief.", encoding="utf-8")

        discovered = await plugin_command("discover", cwd=str(tmp_path))
        reloaded = await reload_plugins(cwd=str(tmp_path))
        registered = await plugin_command(
            "register_builtin",
            plugin_id="builtin_demo",
            definition={"name": "Builtin Demo"},
        )
        styles = await output_style("list", cwd=str(tmp_path))
        style = await output_style("read", name="brief", cwd=str(tmp_path))
        saved = await workflow("save", name="hello", command="echo hello", cwd=str(tmp_path))
        workflows = await workflow("list", cwd=str(tmp_path))
        ran = await workflow("run", name="hello", cwd=str(tmp_path))

        assert discovered["count"] == 1
        assert reloaded["reloaded"] == 1
        assert registered["id"] == "builtin_demo"
        assert styles["count"] == 1
        assert style["content"] == "Be brief."
        assert saved["name"] == "hello"
        assert workflows["count"] == 1
        assert "hello" in ran["stdout"]

    asyncio.run(run())


def test_paths_cannot_escape_workspace(tmp_path: Path):
    with pytest.raises(PermissionError):
        resolve_workspace_path("../outside.txt", cwd=str(tmp_path))


def test_bash_command_classification():
    assert detectBlockedSleepPattern("sleep 999")
    assert ps_blocked_sleep("Start-Sleep 999")
    assert isSearchOrReadBashCommand("rg hello")["isSearch"]


def test_shell_permission_and_safety_helpers(tmp_path: Path):
    async def run() -> None:
        assert isCommandSafeViaFlagParsing("rg hello .")
        assert not isCommandSafeViaFlagParsing("rm -rf build")
        assert getSimpleCommandPrefix("env FOO=1 git status --short") == "git status"
        assert getDestructiveCommandWarning("git reset --hard") is not None
        assert checkPathConstraints("cat ./README.md", cwd=str(tmp_path))["ok"]
        assert not checkPathConstraints("cat ../outside.txt", cwd=str(tmp_path))["ok"]
        assert checkPermissionMode("rg hello", mode="read-only")["allowed"]
        assert not checkPermissionMode("python build.py", mode="read-only")["allowed"]

        permitted = await bashToolHasPermission("rg hello", read_only_mode=True)
        denied = await bashToolHasPermission("rm -rf build", read_only_mode=True)
        assert permitted["allowed"]
        assert not denied["allowed"]

    asyncio.run(run())


def test_powershell_permission_and_safety_helpers(tmp_path: Path):
    async def run() -> None:
        assert isReadOnlyCommand("Get-ChildItem | Select-Object Name")
        assert not isReadOnlyCommand("Remove-Item -Recurse build")
        assert powershellCommandIsSafe("Get-Content README.md")
        assert not powershellCommandIsSafe("git reset --hard")
        assert ps_check_path_constraints("Get-Content -Path .\\README.md", cwd=str(tmp_path))["ok"]
        assert not ps_check_path_constraints("Get-Content -Path ..\\outside.txt", cwd=str(tmp_path))["ok"]
        assert ps_check_permission_mode("Get-ChildItem", mode="read-only")["allowed"]
        assert not ps_check_permission_mode("New-Item -ItemType SymbolicLink link target")["allowed"]

        permitted = await powershellToolHasPermission("Get-ChildItem", read_only_mode=True)
        denied = await powershellToolHasPermission("Remove-Item -Recurse build", read_only_mode=True)
        assert permitted["allowed"]
        assert not denied["allowed"]

    asyncio.run(run())


def test_permission_core_loader_hooks_and_filesystem(tmp_path: Path):
    async def run() -> None:
        await _resetForTesting()
        assert not await isAutoModeActive()
        await setAutoModeActive(True)
        assert await isAutoModeActive()
        await setAutoModeCircuitBroken(True)
        assert not await isAutoModeActive()

        assert await permissionModeFromString("read-only") == "readonly"
        assert await permissionModeShortTitle("accept-edits") == "Auto"
        assert await getModeColor("plan") == "cyan"
        assert "允许" in await getRuleBehaviorDescription("allow")

        parsed = await permissionRuleValueFromString("allow:read_file:README.md")
        assert parsed.tool == "read_file"
        assert await permissionRuleValueToString(parsed) == "allow:read_file:README.md"

        saved = await permissions_command("add", rule="allow:read_file:README.md", cwd=str(tmp_path))
        listed = await permissions_command("list", cwd=str(tmp_path))
        checked = await permissions_command("check", tool="read_file", value="README.md", cwd=str(tmp_path))
        denied = await checkRuleBasedPermissions(
            "write_file",
            "secret.txt",
            rules=[{"tool": "write_file", "value": "secret.txt", "behavior": "deny"}],
        )
        read_rule = await createReadRuleSuggestion("notes.md")
        persisted = await persistPermissionUpdate({"rule": read_rule.to_dict()}, cwd=str(tmp_path))

        clearPermissionLog()
        context = createPermissionContext("read_file", "README.md", cwd=str(tmp_path)).to_dict()
        decision = await handleInteractivePermission(context, saved["rules"])

        assert listed["count"] == 1
        assert checked["allowed"]
        assert not denied["allowed"]
        assert any(rule["value"] == "notes.md" for rule in persisted)
        assert decision["behavior"] == "allow"
        assert len(getPermissionLog()) == 1
        assert await pathInWorkingPath("README.md", cwd=str(tmp_path))
        assert not await pathInWorkingPath("../outside.txt", cwd=str(tmp_path))
        assert (await checkReadPermissionForTool("README.md", cwd=str(tmp_path)))["ok"]
        assert not (await checkWritePermissionForTool(".env", cwd=str(tmp_path)))["ok"]
        assert (await getSessionMemoryPath("abc", cwd=str(tmp_path))).endswith("abc.md")
        assert len(await loadAllPermissionRulesFromDisk(str(tmp_path))) == 2

    asyncio.run(run())


def test_git_filesystem_config_gitignore_and_review_helpers(tmp_path: Path):
    async def run() -> None:
        git_dir = tmp_path / ".git"
        refs = git_dir / "refs" / "heads"
        remote_refs = git_dir / "refs" / "remotes" / "origin"
        refs.mkdir(parents=True)
        remote_refs.mkdir(parents=True)
        sha = "a" * 40
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (refs / "main").write_text(sha + "\n", encoding="utf-8")
        (remote_refs / "HEAD").write_text("ref: refs/remotes/origin/main\n", encoding="utf-8")
        (git_dir / "config").write_text(
            '[remote "origin"]\n  url = https://example.com/repo.git\n[core]\n  bare = false\n',
            encoding="utf-8",
        )

        parsed = await parseConfigString((git_dir / "config").read_text(encoding="utf-8"))
        await clearResolveGitDirCache()
        ignored_add = await addFileGlobRuleToGitignore("*.log", cwd=str(tmp_path))
        ignored = await isPathGitignored("debug.log", cwd=str(tmp_path))
        review_gate = await checkOverageGate("abc", max_chars=10)
        over_gate = await checkOverageGate("abc", max_chars=0)
        review = await launchRemoteReview(cwd=str(tmp_path), max_chars=10)

        assert await parseGitConfigValue("true") is True
        assert parsed["remote.origin"]["url"] == "https://example.com/repo.git"
        assert await resolveGitDir(str(tmp_path)) == str(git_dir)
        assert await getCachedBranch(str(tmp_path)) == "main"
        assert await getCachedHead(str(tmp_path)) == sha
        assert await getCachedRemoteUrl(str(tmp_path)) == "https://example.com/repo.git"
        assert await getCachedDefaultBranch(str(tmp_path)) == "main"
        assert await getWorktreeCountFromFs(str(tmp_path)) == 1
        assert await isValidGitSha(sha)
        assert await isSafeRefName("refs/heads/main")
        assert ignored_add["added"] is True
        assert ignored is True
        assert review_gate["allowed"] is True
        assert over_gate["allowed"] is False
        assert "started" in review

    asyncio.run(run())


def test_github_and_branch_command_helpers(tmp_path: Path):
    async def run() -> None:
        git_dir = tmp_path / ".git"
        refs = git_dir / "refs" / "heads"
        refs.mkdir(parents=True)
        sha = "b" * 40
        (git_dir / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
        (refs / "feature").write_text(sha + "\n", encoding="utf-8")

        derived = await deriveFirstPrompt("Write a parser for settings files!")
        current = await branch_call("current", cwd=str(tmp_path))
        listed = await branch_call("list", cwd=str(tmp_path))
        auth = await getGhAuthStatus(cwd=str(tmp_path))
        issues = await issue_command("list", cwd=str(tmp_path), limit=1)
        comments = await pr_comments_command(cwd=str(tmp_path))

        assert derived == "deepseek/write-a-parser-for-settings-files"
        assert current["branch"] == "feature"
        assert "exit_code" in listed
        assert "authenticated" in auth
        assert "available" in issues
        assert "count" in comments

    asyncio.run(run())


def test_settings_config_model_and_status_commands(tmp_path: Path):
    async def run() -> None:
        await resetSettingsCache()
        project_path = tmp_path / ".deepseek_settings.json"
        project_path.write_text(
            '{"model":"deepseek-chat","autoMode":{"enabled":true},"env":{"A":"B"}}',
            encoding="utf-8",
        )
        local_path = tmp_path / ".deepseek.local.json"
        local_path.write_text('{"provider":"deepseek"}', encoding="utf-8")

        validation = await validateSettingsFileContent(project_path.read_text(encoding="utf-8"))
        parsed = await parseSettingsFile(project_path)
        settings = await getInitialSettings(str(tmp_path))
        with_sources = await getSettingsWithSources(str(tmp_path))
        config_get = await config_command("get", key="model", cwd=str(tmp_path))
        config_set = await config_command("set", key="defaultModel", value="deepseek-coder", cwd=str(tmp_path))
        model_current = await model_command("current", cwd=str(tmp_path))
        model_set = await model_command("set", model="deepseek-chat", cwd=str(tmp_path))
        status = await status_command(cwd=str(tmp_path))

        assert validation["ok"]
        assert parsed["settings"]["model"] == "deepseek-chat"
        assert settings["provider"] == "deepseek"
        assert with_sources["errors"] == []
        assert await rawSettingsContainsKey(project_path.read_text(encoding="utf-8"), "model")
        assert (await getSettingsFilePathForSource("project", str(tmp_path))).endswith(".deepseek_settings.json")
        assert await hasAutoModeOptIn(str(tmp_path))
        assert config_get["value"] == "deepseek-chat"
        assert config_set["settings"]["defaultModel"] == "deepseek-coder"
        assert "available_models" in model_current
        assert model_set["model"] == "deepseek-chat"
        assert status["provider"] == "deepseek"
        assert await isMcpServerCommandEntry({"command": "node"})
        assert await isMcpServerUrlEntry({"url": "http://localhost"})

    asyncio.run(run())


def test_deepseek_model_utility_layer():
    async def run() -> None:
        assert await isModelAlias("sonnet")
        assert await isModelFamilyAlias("coding")
        assert await normalizeModelStringForAPI("sonnet") == "deepseek-chat"
        assert await getCanonicalName("coder") == "deepseek-coder"
        assert await getDefaultMainLoopModel() == "deepseek-chat"
        assert await getDefaultOpusModel() == "deepseek-reasoner"
        assert await getBestModel("coding task") == "deepseek-coder"
        assert await getMarketingNameForModel("deepseek-chat") == "DeepSeek Chat"
        assert await resolveSkillModelOverride({"model": "reasoner"}) == "deepseek-reasoner"
        assert (await getModelCapability("deepseek-coder"))["supports_tools"] is True
        refreshed = await refreshModelCapabilities({"deepseek-chat": {"context_window": 128000}})
        assert refreshed["deepseek-chat"]["context_window"] == 128000
        assert (await validateModel("deepseek-chat"))["ok"]
        assert await isModelAllowed("deepseek-chat")
        assert (await getDefaultOptionForUser())["value"] == "deepseek-chat"
        assert any(option["value"] == "deepseek-coder" for option in await getModelOptions())
        assert (await getModelStrings())["deepseek-reasoner"] == "DeepSeek Reasoner"
        assert await resolveOverriddenModel("deepseek-chat", "coder") == "deepseek-coder"
        assert await getAPIProvider() == "deepseek"
        assert await isFirstPartyAnthropicBaseUrl("https://api.deepseek.com")
        assert await getAgentModel("code") == "deepseek-coder"
        assert await getAgentModelDisplay("reasoner") == "DeepSeek Reasoner"
        assert len(await getAgentModelOptions()) >= 3
        assert "Claude model names" in (await getModelDeprecationWarning("claude-3-sonnet"))

    asyncio.run(run())


def test_registry_executes_tool_call(tmp_path: Path):
    async def run() -> None:
        registry = build_default_tool_registry()
        call = InternalToolCall(
            id="call_1",
            name="write_file",
            arguments={"path": "out.txt", "content": "ok", "cwd": str(tmp_path)},
        )
        result = await registry.call(call)

        assert result.role == "tool"
        assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "ok"

    asyncio.run(run())
