"""Capacity wake primitive for bridge poll loops."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(slots=True)
class CapacitySignal:
    event: asyncio.Event

    @property
    def signal(self) -> asyncio.Event:
        return self.event

    def cleanup(self) -> None:
        return None


class CapacityWake:
    def __init__(self, outerSignal: asyncio.Event | None = None) -> None:
        self.outerSignal = outerSignal
        self._wake = asyncio.Event()

    def wake(self) -> None:
        self._wake.set()
        self._wake = asyncio.Event()

    def signal(self) -> CapacitySignal:
        merged = asyncio.Event()
        if self._wake.is_set() or (self.outerSignal and self.outerSignal.is_set()):
            merged.set()
        else:
            asyncio.create_task(self._mirror(merged))
        return CapacitySignal(merged)

    async def _mirror(self, merged: asyncio.Event) -> None:
        tasks = [asyncio.create_task(self._wake.wait())]
        if self.outerSignal:
            tasks.append(asyncio.create_task(self.outerSignal.wait()))
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            merged.set()
        finally:
            for task in tasks:
                task.cancel()


def createCapacityWake(outerSignal: asyncio.Event | None = None) -> CapacityWake:
    return CapacityWake(outerSignal)
