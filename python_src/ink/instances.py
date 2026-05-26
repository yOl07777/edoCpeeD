from __future__ import annotations

from typing import Any

instances: list[Any] = []


def addInstance(instance: Any) -> Any:
    instances.append(instance)
    return instance


def removeInstance(instance: Any) -> bool:
    if instance in instances:
        instances.remove(instance)
        return True
    return False


def getInstances(*args: Any, **kwargs: Any) -> list[Any]:
    return list(instances)


default = instances
_module_migration_placeholder = getInstances
