"""Companion constants and lightweight data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Rarity = Literal["common", "uncommon", "rare", "epic", "legendary"]
Species = Literal[
    "duck",
    "goose",
    "blob",
    "cat",
    "dragon",
    "octopus",
    "owl",
    "penguin",
    "turtle",
    "snail",
    "ghost",
    "axolotl",
    "capybara",
    "cactus",
    "robot",
    "rabbit",
    "mushroom",
    "chonk",
]
Eye = Literal[".", "*", "x", "o", "@", "-"]
Hat = Literal["none", "crown", "tophat", "propeller", "halo", "wizard", "beanie", "tinyduck"]
StatName = Literal["DEBUGGING", "PATIENCE", "CHAOS", "WISDOM", "SNARK"]

duck = "duck"
goose = "goose"
blob = "blob"
cat = "cat"
dragon = "dragon"
octopus = "octopus"
owl = "owl"
penguin = "penguin"
turtle = "turtle"
snail = "snail"
ghost = "ghost"
axolotl = "axolotl"
capybara = "capybara"
cactus = "cactus"
robot = "robot"
rabbit = "rabbit"
mushroom = "mushroom"
chonk = "chonk"

RARITIES: tuple[Rarity, ...] = ("common", "uncommon", "rare", "epic", "legendary")
SPECIES: tuple[Species, ...] = (
    duck,
    goose,
    blob,
    cat,
    dragon,
    octopus,
    owl,
    penguin,
    turtle,
    snail,
    ghost,
    axolotl,
    capybara,
    cactus,
    robot,
    rabbit,
    mushroom,
    chonk,
)
EYES: tuple[Eye, ...] = (".", "*", "x", "o", "@", "-")
HATS: tuple[Hat, ...] = ("none", "crown", "tophat", "propeller", "halo", "wizard", "beanie", "tinyduck")
STAT_NAMES: tuple[StatName, ...] = ("DEBUGGING", "PATIENCE", "CHAOS", "WISDOM", "SNARK")

RARITY_WEIGHTS: dict[Rarity, int] = {"common": 60, "uncommon": 25, "rare": 10, "epic": 4, "legendary": 1}
RARITY_STARS: dict[Rarity, str] = {"common": "*", "uncommon": "**", "rare": "***", "epic": "****", "legendary": "*****"}
RARITY_COLORS: dict[Rarity, str] = {
    "common": "inactive",
    "uncommon": "success",
    "rare": "permission",
    "epic": "autoAccept",
    "legendary": "warning",
}


@dataclass(slots=True)
class CompanionBones:
    rarity: Rarity
    species: Species
    eye: Eye
    hat: Hat
    shiny: bool
    stats: dict[StatName, int] = field(default_factory=dict)


@dataclass(slots=True)
class CompanionSoul:
    name: str
    personality: str


@dataclass(slots=True)
class Companion:
    rarity: Rarity
    species: Species
    eye: Eye
    hat: Hat
    shiny: bool
    stats: dict[StatName, int] = field(default_factory=dict)
    name: str = "Buddy"
    personality: str = ""
    hatchedAt: int = 0
