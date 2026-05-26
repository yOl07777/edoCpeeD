"""ASCII companion sprite rendering."""

from __future__ import annotations

from .types import CompanionBones, Species

DEFAULT_FRAMES: dict[str, list[list[str]]] = {
    "duck": [["    __    ", "  <({E})__ ", "   (  ._>", "    `--'  "], ["    __    ", "  <({E})__ ", "   (  ._>", "    `--'~ "]],
    "cat": [["  /\\_/\\  ", " ( {E} {E} ) ", " (  w  ) ", " (\")_(\") "]],
    "robot": [["  .[||]. ", " [ {E}{E} ] ", " [ ====] ", " `------'"]],
    "ghost": [["  .----. ", " / {E}{E} \\ ", " |      | ", " ~`~~`~ "]],
    "dragon": [[" /^\\ /^\\ ", "< {E} {E} >", "(  ~~  )", "`-vvv-' "]],
}
FALLBACK_FRAME = [["  .----. ", " ( {E}{E} ) ", " (      ) ", " `----'  "]]
HAT_LINES = {
    "none": "",
    "crown": "  \\^^^/  ",
    "tophat": "  [___]  ",
    "propeller": "   -+-   ",
    "halo": "  (   )  ",
    "wizard": "   /^\\   ",
    "beanie": "  (___)  ",
    "tinyduck": "   ,>    ",
}


def _as_bones(bones: CompanionBones | dict) -> dict:
    if isinstance(bones, dict):
        return bones
    return {
        "rarity": bones.rarity,
        "species": bones.species,
        "eye": bones.eye,
        "hat": bones.hat,
        "shiny": bones.shiny,
        "stats": bones.stats,
    }


def renderSprite(bones: CompanionBones | dict, frame: int = 0) -> list[str]:
    data = _as_bones(bones)
    species = str(data.get("species") or "blob")
    frames = DEFAULT_FRAMES.get(species, FALLBACK_FRAME)
    body = [line.replace("{E}", str(data.get("eye") or ".")) for line in frames[frame % len(frames)]]
    hat = str(data.get("hat") or "none")
    hat_line = HAT_LINES.get(hat, "")
    if hat_line:
        return [hat_line, *body]
    return body


def spriteFrameCount(species: Species | str) -> int:
    return len(DEFAULT_FRAMES.get(str(species), FALLBACK_FRAME))


def renderFace(bones: CompanionBones | dict) -> str:
    data = _as_bones(bones)
    eye = str(data.get("eye") or ".")
    species = str(data.get("species") or "blob")
    if species in {"duck", "goose"}:
        return f"({eye}>"
    if species == "cat":
        return f"={eye}w{eye}="
    if species == "dragon":
        return f"<{eye}~{eye}>"
    if species == "robot":
        return f"[{eye}{eye}]"
    if species == "ghost":
        return f"/{eye}{eye}\\"
    return f"({eye}{eye})"
