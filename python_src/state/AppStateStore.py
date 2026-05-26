"""Default application state for the Python DeepSeek runtime."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


IDLE_SPECULATION_STATE: dict[str, str] = {"status": "idle"}


def getDefaultAppState() -> dict[str, Any]:
    """Return a fresh AppState-shaped dict.

    The TypeScript source defines a large React-facing state tree.  The Python
    terminal only needs a serializable subset, but keeping the same top-level
    keys lets migrated selectors and task helpers behave like the original.
    """

    return {
        "settings": {},
        "tasks": {},
        "agentNameRegistry": {},
        "verbose": False,
        "mainLoopModel": None,
        "mainLoopModelForSession": None,
        "statusLineText": None,
        "expandedView": "none",
        "isBriefOnly": False,
        "showTeammateMessagePreview": False,
        "selectedIPAgentIndex": -1,
        "coordinatorTaskIndex": -1,
        "viewSelectionMode": "none",
        "footerSelection": None,
        "toolPermissionContext": {
            "mode": "default",
            "additionalDirectories": [],
            "alwaysAllowRules": [],
            "deniedRules": [],
            "askAgainRules": [],
        },
        "agent": None,
        "agentDefinitions": {"activeAgents": [], "allAgents": []},
        "fileHistory": {
            "snapshots": [],
            "trackedFiles": set(),
            "snapshotSequence": 0,
        },
        "attribution": {},
        "mcp": {
            "clients": [],
            "tools": [],
            "commands": [],
            "resources": {},
            "pluginReconnectKey": 0,
        },
        "plugins": {
            "enabled": [],
            "disabled": [],
            "commands": [],
            "errors": [],
            "installationStatus": {"marketplaces": [], "plugins": []},
            "needsRefresh": False,
        },
        "todos": {},
        "remoteAgentTaskSuggestions": [],
        "notifications": {"current": None, "queue": []},
        "elicitation": {"queue": []},
        "thinkingEnabled": True,
        "promptSuggestionEnabled": True,
        "sessionHooks": {},
        "inbox": {"messages": []},
        "workerSandboxPermissions": {"queue": [], "selectedIndex": 0},
        "pendingWorkerRequest": None,
        "pendingSandboxRequest": None,
        "promptSuggestion": {
            "text": None,
            "promptId": None,
            "shownAt": 0,
            "acceptedAt": 0,
            "generationRequestId": None,
        },
        "speculation": deepcopy(IDLE_SPECULATION_STATE),
        "speculationSessionTimeSavedMs": 0,
        "skillImprovement": {"suggestion": None},
        "authVersion": 0,
        "initialMessage": None,
        "effortValue": None,
        "activeOverlays": set(),
        "fastMode": False,
        "viewingAgentTaskId": None,
        "foregroundedTaskId": None,
        "remoteSessionUrl": None,
        "remoteConnectionStatus": "connecting",
        "remoteBackgroundTaskCount": 0,
        "replBridgeEnabled": False,
        "replBridgeExplicit": False,
        "replBridgeOutboundOnly": False,
        "replBridgeConnected": False,
        "replBridgeSessionActive": False,
        "replBridgeReconnecting": False,
        "replBridgeConnectUrl": None,
        "replBridgeSessionUrl": None,
        "replBridgeEnvironmentId": None,
        "replBridgeSessionId": None,
        "replBridgeError": None,
        "replBridgeInitialName": None,
        "showRemoteCallout": False,
        "kairosEnabled": False,
    }


__all__ = ["IDLE_SPECULATION_STATE", "getDefaultAppState"]
