from __future__ import annotations

from typing import Any

from python_src.memdir.memdir import buildMemoryPrompt, ensureMemoryDirExists
from python_src.tools.base import PythonTool, object_schema


async def memory_command(
    action: str,
    *,
    content: str | None = None,
    path: str = ".deepseek_memory",
    cwd: str | None = None,
) -> dict[str, Any]:
    directory = ensureMemoryDirExists(path, cwd=cwd)
    entrypoint = directory / "MEMORY.md"
    if action == "read":
        return {"path": str(entrypoint), "content": entrypoint.read_text(encoding="utf-8", errors="replace")}
    if action == "append":
        if not content:
            raise ValueError("content is required for append")
        with entrypoint.open("a", encoding="utf-8") as handle:
            handle.write("\n" + content.strip() + "\n")
        return {"path": str(entrypoint), "appended": content.strip()}
    if action == "prompt":
        return {"prompt": buildMemoryPrompt(path, cwd=cwd)}
    raise ValueError(f"Unknown memory action: {action}")


call = PythonTool(
    name="memory",
    description="Read, append, or render local project memory.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["read", "append", "prompt"]},
            "content": {"type": "string"},
            "path": {"type": "string", "default": ".deepseek_memory"},
        },
        required=["action"],
    ),
    handler=memory_command,
    read_only=False,
)
