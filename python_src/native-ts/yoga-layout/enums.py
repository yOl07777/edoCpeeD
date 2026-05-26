"""Yoga enum constants ported from ``src/native-ts/yoga-layout/enums.ts``."""

from __future__ import annotations

from types import SimpleNamespace


def _ns(**values: int) -> SimpleNamespace:
    return SimpleNamespace(**values)


Align = _ns(
    Auto=0,
    FlexStart=1,
    Center=2,
    FlexEnd=3,
    Stretch=4,
    Baseline=5,
    SpaceBetween=6,
    SpaceAround=7,
    SpaceEvenly=8,
)
BoxSizing = _ns(BorderBox=0, ContentBox=1)
Dimension = _ns(Width=0, Height=1)
Direction = _ns(Inherit=0, LTR=1, RTL=2)
Display = _ns(Flex=0, None_=1, Contents=2)
setattr(Display, "None", 1)
Edge = _ns(
    Left=0,
    Top=1,
    Right=2,
    Bottom=3,
    Start=4,
    End=5,
    Horizontal=6,
    Vertical=7,
    All=8,
)
Errata = _ns(
    None_=0,
    StretchFlexBasis=1,
    AbsolutePositionWithoutInsetsExcludesPadding=2,
    AbsolutePercentAgainstInnerSize=4,
    All=2147483647,
    Classic=2147483646,
)
setattr(Errata, "None", 0)
ExperimentalFeature = _ns(WebFlexBasis=0)
FlexDirection = _ns(Column=0, ColumnReverse=1, Row=2, RowReverse=3)
Gutter = _ns(Column=0, Row=1, All=2)
Justify = _ns(
    FlexStart=0,
    Center=1,
    FlexEnd=2,
    SpaceBetween=3,
    SpaceAround=4,
    SpaceEvenly=5,
)
MeasureMode = _ns(Undefined=0, Exactly=1, AtMost=2)
Overflow = _ns(Visible=0, Hidden=1, Scroll=2)
PositionType = _ns(Static=0, Relative=1, Absolute=2)
Unit = _ns(Undefined=0, Point=1, Percent=2, Auto=3)
Wrap = _ns(NoWrap=0, Wrap=1, WrapReverse=2)


__all__ = [
    "Align",
    "BoxSizing",
    "Dimension",
    "Direction",
    "Display",
    "Edge",
    "Errata",
    "ExperimentalFeature",
    "FlexDirection",
    "Gutter",
    "Justify",
    "MeasureMode",
    "Overflow",
    "PositionType",
    "Unit",
    "Wrap",
]
