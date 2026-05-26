from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from python_src.components.agents._shared import coerce_agent
from python_src.components.agents.types import AGENT_PATHS


def _config_home() -> Path:
    return Path(os.environ.get("DEEPCODE_CONFIG_HOME") or os.environ.get("DEEPSEEK_CONFIG_HOME") or (Path.home() / ".deepseek"))


def _agent_dir(source: str) -> Path:
    folder = AGENT_PATHS["FOLDER_NAME"]
    agents_dir = AGENT_PATHS["AGENTS_DIR"]
    if source == "userSettings":
        return _config_home() / agents_dir
    if source == "policySettings":
        return _config_home() / "managed" / agents_dir
    if source == "flagSettings":
        raise ValueError("Cannot get directory path for flagSettings agents")
    return Path.cwd() / folder / agents_dir


def _relative_agent_dir(source: str) -> Path:
    if source in {"projectSettings", "localSettings"}:
        return Path(".") / AGENT_PATHS["FOLDER_NAME"] / AGENT_PATHS["AGENTS_DIR"]
    return _agent_dir(source)


def _yaml_escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


async def deleteAgentFromFile(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    if agent["source"] == "built-in":
        raise ValueError("Cannot delete built-in agents")
    file_path = Path(await getActualAgentFilePath(agent))
    try:
        file_path.unlink()
        deleted = True
    except FileNotFoundError:
        deleted = False
    return {"provider": "deepseek", "path": str(file_path), "deleted": deleted}

async def formatAgentAsMarkdown(*args: Any, **kwargs: Any) -> Any:
    agent_type = kwargs.get("agentType") or (args[0] if len(args) > 0 else "deepseek-agent")
    when_to_use = kwargs.get("whenToUse") or (args[1] if len(args) > 1 else "Use this agent when specialized help is needed.")
    tools = kwargs.get("tools") if "tools" in kwargs else (args[2] if len(args) > 2 else None)
    system_prompt = kwargs.get("systemPrompt") or (args[3] if len(args) > 3 else "You are a focused DeepSeek Code subagent.")
    color = kwargs.get("color") or (args[4] if len(args) > 4 else None)
    model = kwargs.get("model") or (args[5] if len(args) > 5 else None)
    memory = kwargs.get("memory") or (args[6] if len(args) > 6 else None)
    effort = kwargs.get("effort") or (args[7] if len(args) > 7 else None)
    lines = ["---", f"name: {agent_type}", f'description: "{_yaml_escape(str(when_to_use))}"']
    if tools is not None and not (isinstance(tools, list) and len(tools) == 1 and tools[0] == "*"):
        lines.append(f"tools: {', '.join(str(tool) for tool in tools)}")
    if model:
        lines.append(f"model: {model}")
    if effort:
        lines.append(f"effort: {effort}")
    if color:
        lines.append(f"color: {color}")
    if memory:
        lines.append(f"memory: {memory}")
    lines.extend(["---", "", str(system_prompt), ""])
    return "\n".join(lines)

async def getActualAgentFilePath(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    if agent["source"] == "built-in":
        return "Built-in"
    if agent["source"] == "plugin":
        raise ValueError("Cannot get file path for plugin agents")
    filename = agent.get("filename") or agent["agentType"]
    return str(_agent_dir(agent["source"]) / f"{filename}.md")

async def getActualRelativeAgentFilePath(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    if agent["source"] == "built-in":
        return "Built-in"
    if agent["source"] == "plugin":
        return f"Plugin: {agent.get('plugin') or 'Unknown'}"
    if agent["source"] == "flagSettings":
        return "CLI argument"
    filename = agent.get("filename") or agent["agentType"]
    return str(_relative_agent_dir(agent["source"]) / f"{filename}.md")

async def getNewAgentFilePath(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    return str(_agent_dir(agent["source"]) / f"{agent['agentType']}.md")

async def getNewRelativeAgentFilePath(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    if agent["source"] == "built-in":
        return "Built-in"
    return str(_relative_agent_dir(agent["source"]) / f"{agent['agentType']}.md")

async def saveAgentToFile(*args: Any, **kwargs: Any) -> Any:
    source = kwargs.get("source") or (args[0] if len(args) > 0 else "projectSettings")
    if source == "built-in":
        raise ValueError("Cannot save built-in agents")
    agent_type = kwargs.get("agentType") or (args[1] if len(args) > 1 else "deepseek-agent")
    when_to_use = kwargs.get("whenToUse") or (args[2] if len(args) > 2 else "Use this agent when specialized help is needed.")
    tools = kwargs.get("tools") if "tools" in kwargs else (args[3] if len(args) > 3 else None)
    system_prompt = kwargs.get("systemPrompt") or (args[4] if len(args) > 4 else "You are a focused DeepSeek Code subagent.")
    check_exists = kwargs.get("checkExists", args[5] if len(args) > 5 else True)
    path = Path(await getNewAgentFilePath({"source": source, "agentType": agent_type}))
    path.parent.mkdir(parents=True, exist_ok=True)
    if check_exists and path.exists():
        raise FileExistsError(f"Agent file already exists: {path}")
    content = await formatAgentAsMarkdown(agent_type, when_to_use, tools, system_prompt, kwargs.get("color"), kwargs.get("model"), kwargs.get("memory"), kwargs.get("effort"))
    path.write_text(content, encoding="utf-8")
    return {"provider": "deepseek", "path": str(path), "written": True, "bytes": len(content.encode("utf-8"))}

async def updateAgentFile(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    if agent["source"] == "built-in":
        raise ValueError("Cannot update built-in agents")
    path = Path(await getActualAgentFilePath(agent))
    path.parent.mkdir(parents=True, exist_ok=True)
    when_to_use = kwargs.get("newWhenToUse") or kwargs.get("whenToUse") or agent["whenToUse"]
    tools = kwargs.get("newTools") if "newTools" in kwargs else agent["tools"]
    system_prompt = kwargs.get("newSystemPrompt") or kwargs.get("systemPrompt") or agent["systemPrompt"]
    content = await formatAgentAsMarkdown(agent["agentType"], when_to_use, tools, system_prompt, kwargs.get("newColor") or agent["color"], kwargs.get("newModel") or agent["model"], kwargs.get("newMemory") or agent["memory"], kwargs.get("newEffort") or agent["effort"])
    path.write_text(content, encoding="utf-8")
    return {"provider": "deepseek", "path": str(path), "updated": True, "bytes": len(content.encode("utf-8"))}


__all__ = [
    "deleteAgentFromFile",
    "formatAgentAsMarkdown",
    "getActualAgentFilePath",
    "getActualRelativeAgentFilePath",
    "getNewAgentFilePath",
    "getNewRelativeAgentFilePath",
    "saveAgentToFile",
    "updateAgentFile",
]
