"""Deterministic companion generation for the Python migration."""

from __future__ import annotations

import os
from typing import Any, Callable

from .types import (
    EYES,
    HATS,
    RARITIES,
    RARITY_WEIGHTS,
    SPECIES,
    STAT_NAMES,
    Companion,
    CompanionBones,
    Hat,
    Rarity,
    StatName,
)

SALT = "friend-2026-401"
RARITY_FLOOR: dict[Rarity, int] = {
    "common": 5,
    "uncommon": 15,
    "rare": 25,
    "epic": 35,
    "legendary": 50,
}
_roll_cache: dict[str, Any] | None = None
_global_config: dict[str, Any] = {}


def setCompanionConfig(config: dict[str, Any] | None) -> None:
    """Set a local config snapshot used by the Python companion helpers."""

    _global_config.clear()
    _global_config.update(config or {})


def _mulberry32(seed: int) -> Callable[[], float]:
    value = seed & 0xFFFFFFFF

    def rng() -> float:
        nonlocal value
        value = (value + 0x6D2B79F5) & 0xFFFFFFFF
        t = value
        t = ((t ^ (t >> 15)) * (1 | t)) & 0xFFFFFFFF
        t = (t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rng


def _hash_string(value: str) -> int:
    h = 2166136261
    for char in value:
        h ^= ord(char)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _pick(rng: Callable[[], float], values: tuple[Any, ...]) -> Any:
    return values[min(int(rng() * len(values)), len(values) - 1)]


def _roll_rarity(rng: Callable[[], float]) -> Rarity:
    total = sum(RARITY_WEIGHTS.values())
    value = rng() * total
    for rarity in RARITIES:
        value -= RARITY_WEIGHTS[rarity]
        if value < 0:
            return rarity
    return "common"


def _roll_stats(rng: Callable[[], float], rarity: Rarity) -> dict[StatName, int]:
    floor = RARITY_FLOOR[rarity]
    peak = _pick(rng, STAT_NAMES)
    dump = _pick(rng, STAT_NAMES)
    while dump == peak:
        dump = _pick(rng, STAT_NAMES)
    stats: dict[StatName, int] = {}
    for name in STAT_NAMES:
        if name == peak:
            stats[name] = min(100, floor + 50 + int(rng() * 30))
        elif name == dump:
            stats[name] = max(1, floor - 10 + int(rng() * 15))
        else:
            stats[name] = floor + int(rng() * 40)
    return stats


def _roll_from(rng: Callable[[], float]) -> dict[str, Any]:
    rarity = _roll_rarity(rng)
    hat: Hat = "none" if rarity == "common" else _pick(rng, HATS)
    bones = CompanionBones(
        rarity=rarity,
        species=_pick(rng, SPECIES),
        eye=_pick(rng, EYES),
        hat=hat,
        shiny=rng() < 0.01,
        stats=_roll_stats(rng, rarity),
    )
    return {"bones": bones, "inspirationSeed": int(rng() * 1_000_000_000)}


def roll(userId: str) -> dict[str, Any]:
    global _roll_cache
    key = userId + SALT
    if _roll_cache and _roll_cache.get("key") == key:
        return _roll_cache["value"]
    value = _roll_from(_mulberry32(_hash_string(key)))
    _roll_cache = {"key": key, "value": value}
    return value


def rollWithSeed(seed: str) -> dict[str, Any]:
    return _roll_from(_mulberry32(_hash_string(seed)))


def companionUserId(config: dict[str, Any] | None = None) -> str:
    cfg = config or _global_config
    oauth = cfg.get("oauthAccount") if isinstance(cfg.get("oauthAccount"), dict) else {}
    return str(oauth.get("accountUuid") or cfg.get("userID") or os.getenv("DEEPCODE_USER_ID") or "anon")


def getCompanion(config: dict[str, Any] | None = None) -> Companion | None:
    cfg = config or _global_config
    stored = cfg.get("companion")
    if not isinstance(stored, dict):
        return None
    bones: CompanionBones = roll(companionUserId(cfg))["bones"]
    return Companion(
        rarity=bones.rarity,
        species=bones.species,
        eye=bones.eye,
        hat=bones.hat,
        shiny=bones.shiny,
        stats=dict(bones.stats),
        name=str(stored.get("name") or "Buddy"),
        personality=str(stored.get("personality") or ""),
        hatchedAt=int(stored.get("hatchedAt") or 0),
    )
