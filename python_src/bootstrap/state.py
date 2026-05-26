from __future__ import annotations

import os
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


onSessionSwitch: Callable[[str, str], Any] | None = None


def _new_session_id() -> str:
    return uuid.uuid4().hex


def _initial_state() -> dict[str, Any]:
    cwd = str(Path.cwd())
    return {
        "activeTimeCounter": 0,
        "additionalDirectoriesForClaudeMd": [],
        "afkModeHeaderLatched": False,
        "agentColorMap": {},
        "allowedChannels": [],
        "allowedSettingSources": [],
        "apiKeyFromFd": None,
        "budgetContinuationCount": 0,
        "cacheEditingHeaderLatched": False,
        "cachedClaudeMdContent": None,
        "chromeFlagOverride": None,
        "clientType": "cli",
        "codeEditToolDecisionCounter": 0,
        "commitCounter": 0,
        "costCounter": 0,
        "currentTurnTokenBudget": None,
        "cwdState": cwd,
        "directConnectServerUrl": None,
        "eventLogger": None,
        "fastModeHeaderLatched": False,
        "firstTeleportMessageLogged": False,
        "flagSettingsInline": None,
        "flagSettingsPath": None,
        "hasDevChannels": False,
        "hasExitedPlanMode": False,
        "hasUnknownModelCost": False,
        "initJsonSchema": None,
        "initialMainLoopModel": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
        "inlinePlugins": [],
        "inMemoryErrorLog": [],
        "invokedSkills": set(),
        "invokedSkillsByAgent": {},
        "isInteractive": True,
        "isNonInteractiveSession": False,
        "isRemoteMode": False,
        "isScrollDraining": False,
        "kairosActive": False,
        "lastAPIRequest": None,
        "lastAPIRequestMessages": [],
        "lastApiCompletionTimestamp": None,
        "lastClassifierRequests": [],
        "lastEmittedDate": None,
        "lastInteractionTime": time.time(),
        "lastMainRequestId": None,
        "locCounter": 0,
        "loggerProvider": None,
        "lspRecommendationShownThisSession": False,
        "mainLoopModelOverride": None,
        "mainThreadAgentType": None,
        "meter": None,
        "meterProvider": None,
        "modelStrings": {
            "default": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
            "main": os.getenv("DEFAULT_MODEL", "deepseek-chat"),
            "fast": "deepseek-chat",
            "coder": "deepseek-coder",
        },
        "modelUsage": {},
        "needsAutoModeExitAttachment": False,
        "needsPlanModeExitAttachment": False,
        "oauthTokenFromFd": None,
        "originalCwd": cwd,
        "parentSessionId": None,
        "planSlugCache": {},
        "postCompaction": False,
        "prCounter": 0,
        "projectRoot": cwd,
        "promptCache1hAllowlist": [],
        "promptCache1hEligible": False,
        "promptId": None,
        "questionPreviewFormat": None,
        "registeredHooks": [],
        "registeredPluginHooks": [],
        "scheduledTasksEnabled": True,
        "sdkAgentProgressSummariesEnabled": False,
        "sdkBetas": [],
        "sessionBypassPermissionsMode": None,
        "sessionCounter": 0,
        "sessionCreatedTeams": [],
        "sessionCronTasks": [],
        "sessionId": _new_session_id(),
        "sessionIngressToken": None,
        "sessionPersistenceDisabled": False,
        "sessionProjectDir": cwd,
        "sessionSource": "local",
        "sessionTrustAccepted": False,
        "slowOperations": [],
        "statsStore": {},
        "strictToolResultPairing": False,
        "systemPromptSectionCache": {},
        "teleportedSessionInfo": None,
        "thinkingClearLatched": False,
        "tokenCounter": 0,
        "totalAPIDuration": 0,
        "totalAPIDurationWithoutRetries": 0,
        "totalCacheCreationInputTokens": 0,
        "totalCacheReadInputTokens": 0,
        "totalCostUSD": 0.0,
        "totalDuration": 0,
        "totalInputTokens": 0,
        "totalLinesAdded": 0,
        "totalLinesRemoved": 0,
        "totalOutputTokens": 0,
        "totalToolDuration": 0,
        "totalWebSearchRequests": 0,
        "tracerProvider": None,
        "turnClassifierCount": 0,
        "turnClassifierDurationMs": 0,
        "turnHookCount": 0,
        "turnHookDurationMs": 0,
        "turnOutputTokens": 0,
        "turnToolCount": 0,
        "turnToolDurationMs": 0,
        "useCoworkPlugins": False,
        "userMsgOptIn": False,
    }


_STATE: dict[str, Any] = _initial_state()


def _clone(value: Any) -> Any:
    if isinstance(value, set):
        return set(value)
    try:
        return deepcopy(value)
    except Exception:
        return value


def _key_from_accessor(name: str, prefix_len: int) -> str:
    stem = name[prefix_len:]
    return stem[:1].lower() + stem[1:]


def peekState(key: str | None = None, default: Any = None) -> Any:
    if key is None:
        return _clone(_STATE)
    return _clone(_STATE.get(key, default))


def setStateValue(key: str, value: Any) -> Any:
    _STATE[key] = value
    return value


def getStateSnapshot() -> dict[str, Any]:
    return peekState()


def resetStateForTests() -> dict[str, Any]:
    global _STATE
    _STATE = _initial_state()
    return getStateSnapshot()


def resetSdkInitState() -> None:
    for key in ("sdkBetas", "sdkAgentProgressSummariesEnabled", "initJsonSchema"):
        _STATE[key] = _initial_state()[key]


def resetModelStringsForTestingOnly() -> dict[str, str]:
    _STATE["modelStrings"] = _initial_state()["modelStrings"]
    return _clone(_STATE["modelStrings"])


def resetCostState() -> None:
    for key in (
        "costCounter",
        "totalCostUSD",
        "totalInputTokens",
        "totalOutputTokens",
        "totalCacheCreationInputTokens",
        "totalCacheReadInputTokens",
        "modelUsage",
    ):
        _STATE[key] = _initial_state()[key]


def resetTotalDurationStateAndCost_FOR_TESTS_ONLY() -> None:
    resetCostState()
    for key in ("totalDuration", "totalAPIDuration", "totalAPIDurationWithoutRetries", "totalToolDuration"):
        _STATE[key] = 0


def setCostStateForRestore(state: dict[str, Any]) -> dict[str, Any]:
    for key, value in state.items():
        if key in _STATE:
            _STATE[key] = value
    return getStateSnapshot()


def addInvokedSkill(skill: str, agentId: str | None = None) -> list[str]:
    _STATE["invokedSkills"].add(skill)
    if agentId:
        _STATE["invokedSkillsByAgent"].setdefault(agentId, set()).add(skill)
    return sorted(_STATE["invokedSkills"])


def getInvokedSkills() -> list[str]:
    return sorted(_STATE["invokedSkills"])


def getInvokedSkillsForAgent(agentId: str) -> list[str]:
    return sorted(_STATE["invokedSkillsByAgent"].get(agentId, set()))


def clearInvokedSkills() -> None:
    _STATE["invokedSkills"].clear()
    _STATE["invokedSkillsByAgent"].clear()


def clearInvokedSkillsForAgent(agentId: str) -> None:
    _STATE["invokedSkillsByAgent"].pop(agentId, None)


def addSessionCronTask(task: Any) -> list[Any]:
    _STATE["sessionCronTasks"].append(task)
    return _clone(_STATE["sessionCronTasks"])


def removeSessionCronTasks(predicate: Callable[[Any], bool] | None = None) -> list[Any]:
    if predicate is None:
        _STATE["sessionCronTasks"] = []
    else:
        _STATE["sessionCronTasks"] = [task for task in _STATE["sessionCronTasks"] if not predicate(task)]
    return _clone(_STATE["sessionCronTasks"])


def addSlowOperation(operation: Any) -> list[Any]:
    _STATE["slowOperations"].append(operation)
    return _clone(_STATE["slowOperations"])


def addToInMemoryErrorLog(error: Any) -> list[Any]:
    _STATE["inMemoryErrorLog"].append(error)
    _STATE["inMemoryErrorLog"] = _STATE["inMemoryErrorLog"][-100:]
    return _clone(_STATE["inMemoryErrorLog"])


def addToToolDuration(ms: int | float) -> int | float:
    _STATE["totalToolDuration"] += ms
    _STATE["turnToolDurationMs"] += ms
    _STATE["turnToolCount"] += 1
    return _STATE["totalToolDuration"]


def addToTotalCostState(cost: int | float) -> float:
    _STATE["totalCostUSD"] += float(cost)
    _STATE["costCounter"] += float(cost)
    return float(_STATE["totalCostUSD"])


def addToTotalDurationState(ms: int | float) -> int | float:
    _STATE["totalDuration"] += ms
    return _STATE["totalDuration"]


def addToTotalLinesChanged(added: int = 0, removed: int = 0) -> dict[str, int]:
    _STATE["totalLinesAdded"] += int(added)
    _STATE["totalLinesRemoved"] += int(removed)
    _STATE["locCounter"] += int(added) + int(removed)
    return {"added": _STATE["totalLinesAdded"], "removed": _STATE["totalLinesRemoved"]}


def addToTurnClassifierDuration(ms: int | float) -> int | float:
    _STATE["turnClassifierDurationMs"] += ms
    _STATE["turnClassifierCount"] += 1
    return _STATE["turnClassifierDurationMs"]


def addToTurnHookDuration(ms: int | float) -> int | float:
    _STATE["turnHookDurationMs"] += ms
    _STATE["turnHookCount"] += 1
    return _STATE["turnHookDurationMs"]


def clearBetaHeaderLatches() -> None:
    for key in ("afkModeHeaderLatched", "cacheEditingHeaderLatched", "fastModeHeaderLatched", "thinkingClearLatched"):
        _STATE[key] = False


def clearRegisteredHooks() -> None:
    _STATE["registeredHooks"] = []


def clearRegisteredPluginHooks() -> None:
    _STATE["registeredPluginHooks"] = []


def registerHookCallbacks(callbacks: Any, plugin: bool = False) -> list[Any]:
    key = "registeredPluginHooks" if plugin else "registeredHooks"
    if isinstance(callbacks, list):
        _STATE[key].extend(callbacks)
    else:
        _STATE[key].append(callbacks)
    return _clone(_STATE[key])


def clearSystemPromptSectionState() -> None:
    _STATE["systemPromptSectionCache"] = {}


def setSystemPromptSectionCacheEntry(section: str, value: Any) -> dict[str, Any]:
    _STATE["systemPromptSectionCache"][section] = value
    return _clone(_STATE["systemPromptSectionCache"])


def markPostCompaction() -> None:
    _STATE["postCompaction"] = True


def consumePostCompaction() -> bool:
    value = bool(_STATE["postCompaction"])
    _STATE["postCompaction"] = False
    return value


def flushInteractionTime() -> float:
    now = time.time()
    _STATE["activeTimeCounter"] += max(0, now - float(_STATE["lastInteractionTime"]))
    _STATE["lastInteractionTime"] = now
    return _STATE["activeTimeCounter"]


def updateLastInteractionTime() -> float:
    _STATE["lastInteractionTime"] = time.time()
    return _STATE["lastInteractionTime"]


def markScrollActivity() -> None:
    _STATE["isScrollDraining"] = True
    _STATE["lastScrollActivity"] = time.time()


def waitForScrollIdle() -> bool:
    _STATE["isScrollDraining"] = False
    return True


def handleAutoModeTransition(active: bool | None = None) -> bool:
    if active is not None:
        _STATE["needsAutoModeExitAttachment"] = bool(active)
    return bool(_STATE["needsAutoModeExitAttachment"])


def handlePlanModeTransition(active: bool | None = None) -> bool:
    if active is not None:
        _STATE["needsPlanModeExitAttachment"] = bool(active)
        if not active:
            _STATE["hasExitedPlanMode"] = True
    return bool(_STATE["needsPlanModeExitAttachment"])


def hasExitedPlanModeInSession() -> bool:
    return bool(_STATE["hasExitedPlanMode"])


def hasShownLspRecommendationThisSession() -> bool:
    return bool(_STATE["lspRecommendationShownThisSession"])


def setLspRecommendationShownThisSession(value: bool = True) -> bool:
    _STATE["lspRecommendationShownThisSession"] = bool(value)
    return bool(_STATE["lspRecommendationShownThisSession"])


def hasUnknownModelCost() -> bool:
    return bool(_STATE["hasUnknownModelCost"])


def incrementBudgetContinuationCount() -> int:
    _STATE["budgetContinuationCount"] += 1
    return int(_STATE["budgetContinuationCount"])


def isSessionPersistenceDisabled() -> bool:
    return bool(_STATE["sessionPersistenceDisabled"])


def markFirstTeleportMessageLogged() -> bool:
    _STATE["firstTeleportMessageLogged"] = True
    return True


def needsAutoModeExitAttachment() -> bool:
    return bool(_STATE["needsAutoModeExitAttachment"])


def needsPlanModeExitAttachment() -> bool:
    return bool(_STATE["needsPlanModeExitAttachment"])


def preferThirdPartyAuthentication() -> bool:
    return os.getenv("DEEPSEEK_PREFER_THIRD_PARTY_AUTH", "").lower() in {"1", "true", "yes"}


def regenerateSessionId() -> str:
    old_id = _STATE["sessionId"]
    new_id = _new_session_id()
    _STATE["parentSessionId"] = old_id
    _STATE["sessionId"] = new_id
    return new_id


def switchSession(sessionId: str | None = None) -> str:
    old_id = _STATE["sessionId"]
    new_id = sessionId or _new_session_id()
    _STATE["parentSessionId"] = old_id
    _STATE["sessionId"] = new_id
    if onSessionSwitch is not None:
        onSessionSwitch(old_id, new_id)
    return new_id


def snapshotOutputTokensForTurn() -> int:
    _STATE["turnOutputTokens"] = int(_STATE["totalOutputTokens"])
    return int(_STATE["turnOutputTokens"])


def getUsageForModel(model: str) -> dict[str, Any]:
    return _clone(
        _STATE["modelUsage"].setdefault(
            model,
            {"inputTokens": 0, "outputTokens": 0, "cacheCreationInputTokens": 0, "cacheReadInputTokens": 0, "costUSD": 0.0},
        )
    )


def resetTurnClassifierDuration() -> None:
    _STATE["turnClassifierDurationMs"] = 0
    _STATE["turnClassifierCount"] = 0


def resetTurnHookDuration() -> None:
    _STATE["turnHookDurationMs"] = 0
    _STATE["turnHookCount"] = 0


def resetTurnToolDuration() -> None:
    _STATE["turnToolDurationMs"] = 0
    _STATE["turnToolCount"] = 0


_GETTER_NAMES = [
    "getActiveTimeCounter",
    "getAdditionalDirectoriesForClaudeMd",
    "getAfkModeHeaderLatched",
    "getAgentColorMap",
    "getAllowedChannels",
    "getAllowedSettingSources",
    "getApiKeyFromFd",
    "getBudgetContinuationCount",
    "getCacheEditingHeaderLatched",
    "getCachedClaudeMdContent",
    "getChromeFlagOverride",
    "getClientType",
    "getCodeEditToolDecisionCounter",
    "getCommitCounter",
    "getCostCounter",
    "getCurrentTurnTokenBudget",
    "getCwdState",
    "getDirectConnectServerUrl",
    "getEventLogger",
    "getFastModeHeaderLatched",
    "getFlagSettingsInline",
    "getFlagSettingsPath",
    "getHasDevChannels",
    "getInitJsonSchema",
    "getInitialMainLoopModel",
    "getInlinePlugins",
    "getIsInteractive",
    "getIsNonInteractiveSession",
    "getIsRemoteMode",
    "getIsScrollDraining",
    "getKairosActive",
    "getLastAPIRequest",
    "getLastAPIRequestMessages",
    "getLastApiCompletionTimestamp",
    "getLastClassifierRequests",
    "getLastEmittedDate",
    "getLastInteractionTime",
    "getLastMainRequestId",
    "getLocCounter",
    "getLoggerProvider",
    "getMainLoopModelOverride",
    "getMainThreadAgentType",
    "getMeter",
    "getMeterProvider",
    "getModelStrings",
    "getModelUsage",
    "getOauthTokenFromFd",
    "getOriginalCwd",
    "getParentSessionId",
    "getPlanSlugCache",
    "getPrCounter",
    "getProjectRoot",
    "getPromptCache1hAllowlist",
    "getPromptCache1hEligible",
    "getPromptId",
    "getQuestionPreviewFormat",
    "getRegisteredHooks",
    "getScheduledTasksEnabled",
    "getSdkAgentProgressSummariesEnabled",
    "getSdkBetas",
    "getSessionBypassPermissionsMode",
    "getSessionCounter",
    "getSessionCreatedTeams",
    "getSessionCronTasks",
    "getSessionId",
    "getSessionIngressToken",
    "getSessionProjectDir",
    "getSessionSource",
    "getSessionTrustAccepted",
    "getSlowOperations",
    "getStatsStore",
    "getStrictToolResultPairing",
    "getSystemPromptSectionCache",
    "getTeleportedSessionInfo",
    "getThinkingClearLatched",
    "getTokenCounter",
    "getTotalAPIDuration",
    "getTotalAPIDurationWithoutRetries",
    "getTotalCacheCreationInputTokens",
    "getTotalCacheReadInputTokens",
    "getTotalCostUSD",
    "getTotalDuration",
    "getTotalInputTokens",
    "getTotalLinesAdded",
    "getTotalLinesRemoved",
    "getTotalOutputTokens",
    "getTotalToolDuration",
    "getTotalWebSearchRequests",
    "getTracerProvider",
    "getTurnClassifierCount",
    "getTurnClassifierDurationMs",
    "getTurnHookCount",
    "getTurnHookDurationMs",
    "getTurnOutputTokens",
    "getTurnToolCount",
    "getTurnToolDurationMs",
    "getUseCoworkPlugins",
    "getUserMsgOptIn",
]

_SETTER_NAMES = [
    "setAdditionalDirectoriesForClaudeMd",
    "setAfkModeHeaderLatched",
    "setAllowedChannels",
    "setAllowedSettingSources",
    "setApiKeyFromFd",
    "setCacheEditingHeaderLatched",
    "setCachedClaudeMdContent",
    "setChromeFlagOverride",
    "setClientType",
    "setCwdState",
    "setDirectConnectServerUrl",
    "setEventLogger",
    "setFastModeHeaderLatched",
    "setFlagSettingsInline",
    "setFlagSettingsPath",
    "setHasDevChannels",
    "setHasExitedPlanMode",
    "setHasUnknownModelCost",
    "setInitJsonSchema",
    "setInitialMainLoopModel",
    "setInlinePlugins",
    "setIsInteractive",
    "setIsRemoteMode",
    "setKairosActive",
    "setLastAPIRequest",
    "setLastAPIRequestMessages",
    "setLastApiCompletionTimestamp",
    "setLastClassifierRequests",
    "setLastEmittedDate",
    "setLastMainRequestId",
    "setLoggerProvider",
    "setMainLoopModelOverride",
    "setMainThreadAgentType",
    "setMeter",
    "setMeterProvider",
    "setModelStrings",
    "setNeedsAutoModeExitAttachment",
    "setNeedsPlanModeExitAttachment",
    "setOauthTokenFromFd",
    "setOriginalCwd",
    "setProjectRoot",
    "setPromptCache1hAllowlist",
    "setPromptCache1hEligible",
    "setPromptId",
    "setQuestionPreviewFormat",
    "setScheduledTasksEnabled",
    "setSdkAgentProgressSummariesEnabled",
    "setSdkBetas",
    "setSessionBypassPermissionsMode",
    "setSessionIngressToken",
    "setSessionPersistenceDisabled",
    "setSessionSource",
    "setSessionTrustAccepted",
    "setStatsStore",
    "setStrictToolResultPairing",
    "setTeleportedSessionInfo",
    "setThinkingClearLatched",
    "setTracerProvider",
    "setUseCoworkPlugins",
    "setUserMsgOptIn",
]


def _make_getter(name: str):
    key = _key_from_accessor(name, 3)

    def getter() -> Any:
        return _clone(_STATE.get(key))

    getter.__name__ = name
    return getter


def _make_setter(name: str):
    key = _key_from_accessor(name, 3)

    def setter(value: Any = None) -> Any:
        _STATE[key] = value
        return value

    setter.__name__ = name
    return setter


for _name in _GETTER_NAMES:
    globals().setdefault(_name, _make_getter(_name))

for _name in _SETTER_NAMES:
    globals().setdefault(_name, _make_setter(_name))


__all__ = sorted(name for name in globals() if name.startswith(("get", "set", "add", "clear", "reset", "mark", "handle", "has", "is", "needs", "prefer", "regenerate", "register", "remove", "snapshot", "switch", "update", "wait", "consume", "flush", "peek")))
