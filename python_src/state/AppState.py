"""React AppState compatibility layer for Python code."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .AppStateStore import IDLE_SPECULATION_STATE, getDefaultAppState
from .store import Store, createStore


_default_store: Store[dict[str, Any]] = createStore(getDefaultAppState())
AppStoreContext: dict[str, Store[dict[str, Any]] | None] = {"store": _default_store}


def AppStateProvider(
    children: Any = None,
    initialState: dict[str, Any] | None = None,
    onChangeAppState: Callable[[dict[str, Any]], None] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Create and install an AppState store.

    Python has no React context, so the provider returns a small descriptor and
    updates the module-level context used by the hook shims.
    """

    store = createStore(initialState or getDefaultAppState(), onChangeAppState)
    AppStoreContext["store"] = store
    return {"type": "AppStateProvider", "store": store, "children": children}


def useAppState(selector: Callable[[dict[str, Any]], Any] | None = None) -> Any:
    state = useAppStateStore().getState()
    return selector(state) if selector else state


def useSetAppState() -> Callable[[Any], None]:
    return useAppStateStore().setState


def useAppStateStore() -> Store[dict[str, Any]]:
    store = AppStoreContext.get("store")
    if store is None:
        raise ReferenceError("useAppState/useSetAppState called without AppStateProvider")
    return store


def useAppStateMaybeOutsideOfProvider(selector: Callable[[dict[str, Any]], Any] | None = None) -> Any:
    store = AppStoreContext.get("store")
    if store is None:
        return None
    state = store.getState()
    return selector(state) if selector else state


__all__ = [
    "AppStoreContext",
    "AppStateProvider",
    "IDLE_SPECULATION_STATE",
    "getDefaultAppState",
    "useAppState",
    "useAppStateMaybeOutsideOfProvider",
    "useAppStateStore",
    "useSetAppState",
]
