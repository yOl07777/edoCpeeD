from __future__ import annotations

from typing import Any


OPERATORS = {"d": "delete", "c": "change", "y": "yank"}
SIMPLE_MOTIONS = {"h", "l", "j", "k", "w", "b", "e", "W", "B", "E", "0", "^", "$"}
FIND_KEYS = {"f", "F", "t", "T"}
TEXT_OBJ_SCOPES = {"i": "inner", "a": "around"}
TEXT_OBJ_TYPES = {"w", "W", '"', "'", "`", "(", ")", "b", "[", "]", "{", "}", "B", "<", ">"}
MAX_VIM_COUNT = 10000


def isOperatorKey(key: str) -> bool:
    return key in OPERATORS


def isTextObjScopeKey(key: str) -> bool:
    return key in TEXT_OBJ_SCOPES


def createInitialVimState() -> dict[str, Any]:
    return {"mode": "INSERT", "insertedText": ""}


def createInitialPersistentState() -> dict[str, Any]:
    return {"lastChange": None, "lastFind": None, "register": "", "registerIsLinewise": False}
