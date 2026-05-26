"""Dialog launcher shims for the non-React DeepSeek runtime."""

from __future__ import annotations

from typing import Any

from python_src.interactiveHelpers import showDialog


async def _launch(name: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    result = await showDialog(name, *args, **kwargs)
    result.update(
        {
            "launcher": name,
            "provider": "deepseek",
            "ui": "structured-shim",
        }
    )
    return result


async def launchAssistantInstallWizard(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch(
        "assistant_install_wizard",
        *args,
        message=kwargs.pop("message", "Install DeepSeek Code integrations manually from the generated guidance."),
        **kwargs,
    )


async def launchAssistantSessionChooser(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch("assistant_session_chooser", *args, **kwargs)


async def launchInvalidSettingsDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch(
        "invalid_settings",
        *args,
        message=kwargs.pop("message", "Settings could not be parsed; inspect .deepseek/settings.json."),
        defaultAccepted=False,
        **kwargs,
    )


async def launchResumeChooser(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch("resume_chooser", *args, **kwargs)


async def launchSnapshotUpdateDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch("snapshot_update", *args, **kwargs)


async def launchTeleportRepoMismatchDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch(
        "teleport_repo_mismatch",
        *args,
        message=kwargs.pop("message", "The teleported session repository does not match this workspace."),
        defaultAccepted=False,
        **kwargs,
    )


async def launchTeleportResumeWrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await _launch("teleport_resume", *args, **kwargs)


__all__ = [
    "launchAssistantInstallWizard",
    "launchAssistantSessionChooser",
    "launchInvalidSettingsDialog",
    "launchResumeChooser",
    "launchSnapshotUpdateDialog",
    "launchTeleportRepoMismatchDialog",
    "launchTeleportResumeWrapper",
]
