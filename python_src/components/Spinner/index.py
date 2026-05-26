from __future__ import annotations

from python_src.components.Spinner.FlashingChar import FlashingChar
from python_src.components.Spinner.GlimmerMessage import GlimmerMessage
from python_src.components.Spinner.ShimmerChar import ShimmerChar
from python_src.components.Spinner.SpinnerAnimationRow import SpinnerAnimationRow
from python_src.components.Spinner.SpinnerGlyph import SpinnerGlyph
from python_src.components.Spinner.TeammateSpinnerLine import TeammateSpinnerLine
from python_src.components.Spinner.TeammateSpinnerTree import TeammateSpinnerTree
from python_src.components.Spinner.teammateSelectHint import TEAMMATE_SELECT_HINT
from python_src.components.Spinner.useShimmerAnimation import useShimmerAnimation
from python_src.components.Spinner.useStalledAnimation import useStalledAnimation
from python_src.components.Spinner.utils import (
    getDefaultCharacters,
    hueToRgb,
    interpolateColor,
    parseRGB,
    toRGBColor,
)

default = {
    "provider": "deepseek",
    "components": [
        "FlashingChar",
        "GlimmerMessage",
        "ShimmerChar",
        "SpinnerAnimationRow",
        "SpinnerGlyph",
        "TeammateSpinnerLine",
        "TeammateSpinnerTree",
    ],
}


__all__ = [
    "FlashingChar",
    "GlimmerMessage",
    "ShimmerChar",
    "SpinnerAnimationRow",
    "SpinnerGlyph",
    "TEAMMATE_SELECT_HINT",
    "TeammateSpinnerLine",
    "TeammateSpinnerTree",
    "default",
    "getDefaultCharacters",
    "hueToRgb",
    "interpolateColor",
    "parseRGB",
    "toRGBColor",
    "useShimmerAnimation",
    "useStalledAnimation",
]
