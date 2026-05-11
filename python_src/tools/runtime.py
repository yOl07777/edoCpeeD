from __future__ import annotations

from importlib import import_module

from deepseek_code.core.tool_adapter import ToolRegistry

from python_src.commands.clear.conversation import call as ClearConversationTool
from python_src.commands.cost.cost import call as CostTool
from python_src.commands.memory.memory import call as MemoryTool
from python_src.commands.session.session import call as SessionTool
from python_src.tools.AgentTool.AgentTool import AgentTool
from python_src.tools.AskUserQuestionTool.AskUserQuestionTool import AskUserQuestionTool
from python_src.tools.BashTool.BashTool import BashTool
from python_src.tools.ConfigTool.ConfigTool import ConfigTool
from python_src.tools.EnterPlanModeTool.EnterPlanModeTool import EnterPlanModeTool
from python_src.tools.ExitPlanModeTool.ExitPlanModeV2Tool import ExitPlanModeV2Tool
from python_src.tools.FileEditTool.FileEditTool import FileEditTool
from python_src.tools.FileReadTool.FileReadTool import FileReadTool
from python_src.tools.FileWriteTool.FileWriteTool import FileWriteTool
from python_src.tools.GlobTool.GlobTool import GlobTool
from python_src.tools.GrepTool.GrepTool import GrepTool
from python_src.tools.ListMcpResourcesTool.ListMcpResourcesTool import ListMcpResourcesTool
from python_src.tools.LSPTool.LSPTool import LSPTool
from python_src.tools.NotebookEditTool.NotebookEditTool import NotebookEditTool
from python_src.tools.PowerShellTool.PowerShellTool import PowerShellTool
from python_src.tools.ReadMcpResourceTool.ReadMcpResourceTool import ReadMcpResourceTool
from python_src.tools.RemoteTriggerTool.RemoteTriggerTool import RemoteTriggerTool
from python_src.tools.ScheduleCronTool.CronCreateTool import CronCreateTool
from python_src.tools.ScheduleCronTool.CronDeleteTool import CronDeleteTool
from python_src.tools.ScheduleCronTool.CronListTool import CronListTool
from python_src.tools.SkillTool.SkillTool import SkillTool
from python_src.tools.SleepTool.SleepTool import SleepTool
from python_src.tools.MonitorTool.MonitorTool import MonitorTool
from python_src.tools.TaskCreateTool.TaskCreateTool import TaskCreateTool
from python_src.tools.TaskGetTool.TaskGetTool import TaskGetTool
from python_src.tools.TaskListTool.TaskListTool import TaskListTool
from python_src.tools.TaskOutputTool.TaskOutputTool import TaskOutputTool
from python_src.tools.TaskStopTool.TaskStopTool import TaskStopTool
from python_src.tools.TaskUpdateTool.TaskUpdateTool import TaskUpdateTool
from python_src.tools.TeamCreateTool.TeamCreateTool import TeamCreateTool
from python_src.tools.TeamDeleteTool.TeamDeleteTool import TeamDeleteTool
from python_src.tools.TodoWriteTool.TodoWriteTool import TodoWriteTool
from python_src.tools.SendMessageTool.SendMessageTool import SendMessageTool
from python_src.tools.WebFetchTool.WebFetchTool import WebFetchTool
from python_src.tools.WebSearchTool.WebSearchTool import WebSearchTool
from python_src.tools.WorkflowTool.WorkflowTool import WorkflowTool
from python_src.tools.base import PythonTool

OutputStyleTool = import_module("python_src.commands.output-style.output-style").call
PluginTool = import_module("python_src.commands.plugin.plugin").call
ReloadPluginsTool = import_module("python_src.commands.reload-plugins.reload-plugins").call


DEFAULT_TOOLS: list[PythonTool] = [
    FileReadTool,
    FileWriteTool,
    FileEditTool,
    GlobTool,
    GrepTool,
    BashTool,
    PowerShellTool,
    ConfigTool,
    NotebookEditTool,
    ListMcpResourcesTool,
    ReadMcpResourceTool,
    SkillTool,
    EnterPlanModeTool,
    ExitPlanModeV2Tool,
    LSPTool,
    MemoryTool,
    SessionTool,
    CostTool,
    ClearConversationTool,
    AgentTool,
    SleepTool,
    CronCreateTool,
    CronListTool,
    CronDeleteTool,
    MonitorTool,
    RemoteTriggerTool,
    PluginTool,
    ReloadPluginsTool,
    OutputStyleTool,
    WorkflowTool,
    TeamCreateTool,
    TeamDeleteTool,
    SendMessageTool,
    AskUserQuestionTool,
    TodoWriteTool,
    TaskCreateTool,
    TaskGetTool,
    TaskListTool,
    TaskUpdateTool,
    TaskStopTool,
    TaskOutputTool,
    WebFetchTool,
    WebSearchTool,
]


def get_deepseek_tools() -> list[dict]:
    return [tool.to_deepseek_schema() for tool in DEFAULT_TOOLS]


def build_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in DEFAULT_TOOLS:
        registry.register(tool.name, tool.handler)
    return registry
