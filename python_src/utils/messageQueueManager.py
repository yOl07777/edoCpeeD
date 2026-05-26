"""In-process command queue and notification helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

_COMMAND_QUEUE: list[dict[str, Any]] = []
_PENDING_NOTIFICATIONS: list[dict[str, Any]] = []
_COMMAND_SUBSCRIBERS: list[Callable[[list[dict[str, Any]]], Any]] = []
_NOTIFICATION_SUBSCRIBERS: list[Callable[[list[dict[str, Any]]], Any]] = []


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    if args:
        return {"command": args[0], **kwargs}
    return dict(kwargs)


def _snapshot(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deepcopy(items)


def _notify(subscribers: list[Callable[[list[dict[str, Any]]], Any]], items: list[dict[str, Any]]) -> None:
    snapshot = _snapshot(items)
    for callback in list(subscribers):
        callback(snapshot)


async def isSlashCommand(*args: Any, **kwargs: Any) -> bool:
    value = args[0] if args else kwargs.get("command") or kwargs.get("text") or ""
    if isinstance(value, dict):
        value = value.get("command") or value.get("text") or value.get("input") or ""
    return str(value).lstrip().startswith("/")


async def isPromptInputModeEditable(*args: Any, **kwargs: Any) -> bool:
    mode = str(args[0] if args else kwargs.get("mode") or kwargs.get("inputMode") or "default")
    return mode not in {"locked", "readonly", "read_only", "disabled"}


async def isQueuedCommandEditable(*args: Any, **kwargs: Any) -> bool:
    data = _payload(args, kwargs)
    if "editable" in data:
        return bool(data["editable"])
    if bool(data.get("running") or data.get("inFlight")):
        return False
    return await isPromptInputModeEditable(data.get("mode", "default"))


async def isQueuedCommandVisible(*args: Any, **kwargs: Any) -> bool:
    data = _payload(args, kwargs)
    return bool(data.get("visible", True)) and not bool(data.get("hidden", False))


async def enqueue(*args: Any, **kwargs: Any) -> dict[str, Any]:
    item = _payload(args, kwargs)
    item.setdefault("priority", 0)
    item.setdefault("editable", True)
    item.setdefault("visible", True)
    _COMMAND_QUEUE.append(item)
    _COMMAND_QUEUE.sort(key=lambda entry: int(entry.get("priority", 0)), reverse=True)
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return dict(item)


async def peek(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    return dict(_COMMAND_QUEUE[0]) if _COMMAND_QUEUE else None


async def dequeue(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    if not _COMMAND_QUEUE:
        return None
    item = _COMMAND_QUEUE.pop(0)
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return item


async def dequeueAll(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    items = _snapshot(_COMMAND_QUEUE)
    _COMMAND_QUEUE.clear()
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return items


async def dequeueAllMatching(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    predicate = args[0] if args and callable(args[0]) else kwargs.get("predicate")
    if not callable(predicate):
        key = kwargs.get("key")
        value = kwargs.get("value")
        predicate = lambda item: item.get(key) == value
    matched = [item for item in _COMMAND_QUEUE if predicate(item)]
    _COMMAND_QUEUE[:] = [item for item in _COMMAND_QUEUE if not predicate(item)]
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return _snapshot(matched)


async def remove(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    target_id = args[0] if args else kwargs.get("id") or kwargs.get("command_id")
    for index, item in enumerate(_COMMAND_QUEUE):
        if item.get("id") == target_id:
            removed = _COMMAND_QUEUE.pop(index)
            _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
            return removed
    return None


async def removeByFilter(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    predicate = args[0] if args and callable(args[0]) else kwargs.get("predicate")
    if not callable(predicate):
        return []
    removed = [item for item in _COMMAND_QUEUE if predicate(item)]
    _COMMAND_QUEUE[:] = [item for item in _COMMAND_QUEUE if not predicate(item)]
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return _snapshot(removed)


async def popAllEditable(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    editable = [item for item in _COMMAND_QUEUE if await isQueuedCommandEditable(item)]
    _COMMAND_QUEUE[:] = [item for item in _COMMAND_QUEUE if not await isQueuedCommandEditable(item)]
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return _snapshot(editable)


async def getCommandQueue(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return _snapshot(_COMMAND_QUEUE)


async def getCommandQueueSnapshot(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"count": len(_COMMAND_QUEUE), "commands": _snapshot(_COMMAND_QUEUE)}


async def getCommandQueueLength(*args: Any, **kwargs: Any) -> int:
    return len(_COMMAND_QUEUE)


async def hasCommandsInQueue(*args: Any, **kwargs: Any) -> bool:
    return bool(_COMMAND_QUEUE)


async def getCommandsByMaxPriority(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    if not _COMMAND_QUEUE:
        return []
    max_priority = max(int(item.get("priority", 0)) for item in _COMMAND_QUEUE)
    return [dict(item) for item in _COMMAND_QUEUE if int(item.get("priority", 0)) == max_priority]


async def clearCommandQueue(*args: Any, **kwargs: Any) -> dict[str, int]:
    count = len(_COMMAND_QUEUE)
    _COMMAND_QUEUE.clear()
    _notify(_COMMAND_SUBSCRIBERS, _COMMAND_QUEUE)
    return {"cleared": count}


async def resetCommandQueue(*args: Any, **kwargs: Any) -> dict[str, int]:
    return await clearCommandQueue()


async def recheckCommandQueue(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await getCommandQueueSnapshot()


def subscribeToCommandQueue(callback: Callable[[list[dict[str, Any]]], Any] | None = None) -> Callable[[], None]:
    if callback is None:
        return lambda: None
    _COMMAND_SUBSCRIBERS.append(callback)

    def unsubscribe() -> None:
        if callback in _COMMAND_SUBSCRIBERS:
            _COMMAND_SUBSCRIBERS.remove(callback)

    return unsubscribe


async def enqueuePendingNotification(*args: Any, **kwargs: Any) -> dict[str, Any]:
    item = _payload(args, kwargs)
    item.setdefault("read", False)
    _PENDING_NOTIFICATIONS.append(item)
    _notify(_NOTIFICATION_SUBSCRIBERS, _PENDING_NOTIFICATIONS)
    return dict(item)


async def dequeuePendingNotification(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    if not _PENDING_NOTIFICATIONS:
        return None
    item = _PENDING_NOTIFICATIONS.pop(0)
    _notify(_NOTIFICATION_SUBSCRIBERS, _PENDING_NOTIFICATIONS)
    return item


async def getPendingNotificationsSnapshot(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"count": len(_PENDING_NOTIFICATIONS), "notifications": _snapshot(_PENDING_NOTIFICATIONS)}


def getPendingNotificationsCount() -> int:
    return len(_PENDING_NOTIFICATIONS)


def hasPendingNotifications() -> bool:
    return bool(_PENDING_NOTIFICATIONS)


def clearPendingNotifications() -> dict[str, int]:
    count = len(_PENDING_NOTIFICATIONS)
    _PENDING_NOTIFICATIONS.clear()
    _notify(_NOTIFICATION_SUBSCRIBERS, _PENDING_NOTIFICATIONS)
    return {"cleared": count}


def resetPendingNotifications() -> dict[str, int]:
    return clearPendingNotifications()


def recheckPendingNotifications() -> dict[str, Any]:
    return {"count": len(_PENDING_NOTIFICATIONS), "notifications": _snapshot(_PENDING_NOTIFICATIONS)}


def subscribeToPendingNotifications(callback: Callable[[list[dict[str, Any]]], Any] | None = None) -> Callable[[], None]:
    if callback is None:
        return lambda: None
    _NOTIFICATION_SUBSCRIBERS.append(callback)

    def unsubscribe() -> None:
        if callback in _NOTIFICATION_SUBSCRIBERS:
            _NOTIFICATION_SUBSCRIBERS.remove(callback)

    return unsubscribe


__all__ = [
    "clearCommandQueue",
    "clearPendingNotifications",
    "dequeue",
    "dequeueAll",
    "dequeueAllMatching",
    "dequeuePendingNotification",
    "enqueue",
    "enqueuePendingNotification",
    "getCommandQueue",
    "getCommandQueueLength",
    "getCommandQueueSnapshot",
    "getCommandsByMaxPriority",
    "getPendingNotificationsCount",
    "getPendingNotificationsSnapshot",
    "hasCommandsInQueue",
    "hasPendingNotifications",
    "isPromptInputModeEditable",
    "isQueuedCommandEditable",
    "isQueuedCommandVisible",
    "isSlashCommand",
    "peek",
    "popAllEditable",
    "recheckCommandQueue",
    "recheckPendingNotifications",
    "remove",
    "removeByFilter",
    "resetCommandQueue",
    "resetPendingNotifications",
    "subscribeToCommandQueue",
    "subscribeToPendingNotifications",
]
