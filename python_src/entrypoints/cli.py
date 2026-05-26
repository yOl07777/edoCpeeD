from __future__ import annotations

from typing import Any


async def main(argv: list[str] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "type": "cli_entrypoint",
        "provider": "deepseek",
        "argv": list(argv or kwargs.get("argv", []) or []),
        "module": "deepseek_code.cli",
        "dryRun": bool(kwargs.get("dryRun", True)),
    }


_module_migration_placeholder = main


__all__ = ["main"]
