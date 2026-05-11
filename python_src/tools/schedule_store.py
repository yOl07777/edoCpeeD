from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import count
from typing import Any


_CRON_IDS = count(1)
_MONITOR_IDS = count(1)
_TRIGGER_IDS = count(1)


@dataclass
class CronRecord:
    id: str
    name: str
    prompt: str
    schedule: str
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class MonitorRecord:
    id: str
    name: str
    target: str
    condition: str
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class TriggerRecord:
    id: str
    name: str
    payload: dict[str, Any]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


CRONS: dict[str, CronRecord] = {}
MONITORS: dict[str, MonitorRecord] = {}
TRIGGERS: dict[str, TriggerRecord] = {}


def create_cron(name: str, prompt: str, schedule: str) -> CronRecord:
    record = CronRecord(id=f"cron_{next(_CRON_IDS)}", name=name, prompt=prompt, schedule=schedule)
    CRONS[record.id] = record
    return record


def list_crons(status: str | None = None) -> list[CronRecord]:
    records = list(CRONS.values())
    if status:
        records = [record for record in records if record.status == status]
    return records


def delete_cron(cron_id: str) -> CronRecord:
    try:
        record = CRONS.pop(cron_id)
    except KeyError as exc:
        raise KeyError(f"Unknown cron id: {cron_id}") from exc
    record.status = "deleted"
    return record


def create_monitor(name: str, target: str, condition: str) -> MonitorRecord:
    record = MonitorRecord(id=f"monitor_{next(_MONITOR_IDS)}", name=name, target=target, condition=condition)
    MONITORS[record.id] = record
    return record


def list_monitors(status: str | None = None) -> list[MonitorRecord]:
    records = list(MONITORS.values())
    if status:
        records = [record for record in records if record.status == status]
    return records


def delete_monitor(monitor_id: str) -> MonitorRecord:
    try:
        record = MONITORS.pop(monitor_id)
    except KeyError as exc:
        raise KeyError(f"Unknown monitor id: {monitor_id}") from exc
    record.status = "deleted"
    return record


def create_trigger(name: str, payload: dict[str, Any]) -> TriggerRecord:
    record = TriggerRecord(
        id=f"trigger_{next(_TRIGGER_IDS)}",
        name=name,
        payload=payload,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    TRIGGERS[record.id] = record
    return record


def clear_schedule_state() -> None:
    CRONS.clear()
    MONITORS.clear()
    TRIGGERS.clear()
