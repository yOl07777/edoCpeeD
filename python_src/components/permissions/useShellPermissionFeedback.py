from __future__ import annotations

from typing import Any

from python_src.components.permissions.shellPermissionHelpers import generateShellSuggestionsLabel


async def useShellPermissionFeedback(*args: Any, **kwargs: Any) -> dict[str, Any]:
    command = str(kwargs.get("command") or kwargs.get("cmd") or (args[0] if args else ""))
    return {
        "type": "shell_permission_feedback",
        "provider": "deepseek",
        "command": command,
        "label": await generateShellSuggestionsLabel(command),
        "suggestions": [
            "Review command before allowing it.",
            "Prefer read-only commands when possible.",
            "Avoid destructive flags unless the user explicitly requested them.",
        ],
    }


__all__ = ["useShellPermissionFeedback"]
