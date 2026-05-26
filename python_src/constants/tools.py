from __future__ import annotations


ASYNC_AGENT_ALLOWED_TOOLS = [
    "Read",
    "Glob",
    "Grep",
    "LS",
    "WebSearch",
    "WebFetch",
    "TodoWrite",
]
IN_PROCESS_TEAMMATE_ALLOWED_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Bash",
    "PowerShell",
    "Glob",
    "Grep",
    "TodoWrite",
]
COORDINATOR_MODE_ALLOWED_TOOLS = [
    "Task",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskUpdate",
    "TaskStop",
    "TodoWrite",
]
CUSTOM_AGENT_DISALLOWED_TOOLS = [
    "ScheduleCron",
    "RemoteTrigger",
    "Monitor",
]
ALL_AGENT_DISALLOWED_TOOLS = sorted(set(CUSTOM_AGENT_DISALLOWED_TOOLS))


__all__ = [
    "ALL_AGENT_DISALLOWED_TOOLS",
    "ASYNC_AGENT_ALLOWED_TOOLS",
    "COORDINATOR_MODE_ALLOWED_TOOLS",
    "CUSTOM_AGENT_DISALLOWED_TOOLS",
    "IN_PROCESS_TEAMMATE_ALLOWED_TOOLS",
]
