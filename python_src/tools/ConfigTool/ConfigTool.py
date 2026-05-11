from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.config_store import load_config, save_config


async def config_tool(
    action: str,
    *,
    key: str | None = None,
    value: Any = None,
    path: str = ".deepseek_code_config.json",
    cwd: str | None = None,
) -> dict[str, Any]:
    config = load_config(path, cwd=cwd)
    if action == "get":
        return {"key": key, "value": config.get(key) if key else config}
    if action == "set":
        if not key:
            raise ValueError("key is required for set")
        config[key] = value
        target = save_config(config, path, cwd=cwd)
        return {"path": str(target), "key": key, "value": value}
    if action == "delete":
        if not key:
            raise ValueError("key is required for delete")
        removed = config.pop(key, None)
        target = save_config(config, path, cwd=cwd)
        return {"path": str(target), "key": key, "removed": removed}
    if action == "list":
        return {"config": config}
    raise ValueError(f"Unknown config action: {action}")


ConfigTool = PythonTool(
    name="config",
    description="Read or update local DeepSeek Code configuration.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["get", "set", "delete", "list"]},
            "key": {"type": "string", "description": "Config key."},
            "value": {"description": "Config value for set."},
            "path": {"type": "string", "description": "Workspace-relative config file.", "default": ".deepseek_code_config.json"},
        },
        required=["action"],
    ),
    handler=config_tool,
    read_only=False,
)
