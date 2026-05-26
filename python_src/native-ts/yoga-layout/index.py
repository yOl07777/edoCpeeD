"""Small Python Yoga-layout compatibility layer.

This is not a full flexbox engine. It preserves the API surface the migrated
terminal code imports and computes deterministic row/column layouts for common
Ink-style trees.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

_ENUMS_PATH = Path(__file__).with_name("enums.py")
_spec = importlib.util.spec_from_file_location("_deepcode_yoga_enums", _ENUMS_PATH)
_enums = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_enums)

Align = _enums.Align
BoxSizing = _enums.BoxSizing
Dimension = _enums.Dimension
Direction = _enums.Direction
Display = _enums.Display
Edge = _enums.Edge
Errata = _enums.Errata
ExperimentalFeature = _enums.ExperimentalFeature
FlexDirection = _enums.FlexDirection
Gutter = _enums.Gutter
Justify = _enums.Justify
MeasureMode = _enums.MeasureMode
Overflow = _enums.Overflow
PositionType = _enums.PositionType
Unit = _enums.Unit
Wrap = _enums.Wrap

_COUNTERS = {"calculateLayout": 0, "layoutNode": 0, "measure": 0}


def _value(v: Any, default: float = math.nan) -> float:
    if v is None or v == "auto":
        return default
    if isinstance(v, str) and v.endswith("%"):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class Node:
    @staticmethod
    def create(config: Any | None = None) -> "Node":
        return Node(config)

    @staticmethod
    def createDefault() -> "Node":
        return Node()

    @staticmethod
    def createWithConfig(config: Any) -> "Node":
        return Node(config)

    def __init__(self, config: Any | None = None) -> None:
        self.config = config
        self.children: list[Node] = []
        self.parent: Node | None = None
        self.measure_func: Callable[..., dict[str, float] | tuple[float, float]] | None = None
        self.style: dict[str, Any] = {
            "display": Display.Flex,
            "flexDirection": FlexDirection.Column,
            "alignItems": Align.Stretch,
            "alignSelf": Align.Auto,
            "alignContent": Align.FlexStart,
            "justifyContent": Justify.FlexStart,
            "flexGrow": 0.0,
            "flexShrink": 0.0,
            "flexBasis": None,
            "width": None,
            "height": None,
            "minWidth": None,
            "minHeight": None,
            "maxWidth": None,
            "maxHeight": None,
            "overflow": Overflow.Visible,
            "positionType": PositionType.Relative,
            "direction": Direction.Inherit,
            "flexWrap": Wrap.NoWrap,
            "margin": {},
            "padding": {},
            "border": {},
            "position": {},
            "gap": {},
        }
        self.layout = {"left": 0.0, "top": 0.0, "width": 0.0, "height": 0.0}

    def insertChild(self, child: "Node", index: int) -> None:
        child.parent = self
        self.children.insert(index, child)

    def removeChild(self, child: "Node") -> None:
        self.children.remove(child)
        child.parent = None

    def getChild(self, index: int) -> "Node":
        return self.children[index]

    def getChildCount(self) -> int:
        return len(self.children)

    def getParent(self) -> "Node | None":
        return self.parent

    def free(self) -> None:
        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)
        self.parent = None
        self.children.clear()

    def freeRecursive(self) -> None:
        for child in list(self.children):
            child.freeRecursive()
        self.free()

    def setMeasureFunc(self, fn: Callable[..., Any] | None) -> None:
        self.measure_func = fn

    def unsetMeasureFunc(self) -> None:
        self.measure_func = None

    def calculateLayout(
        self,
        width: float | None = math.nan,
        height: float | None = math.nan,
        direction: int | None = None,
    ) -> None:
        _COUNTERS["calculateLayout"] += 1
        self._layout_tree(_value(width), _value(height), 0.0, 0.0)

    def _layout_tree(self, available_width: float, available_height: float, left: float, top: float) -> None:
        _COUNTERS["layoutNode"] += 1
        width = _value(self.style.get("width"), available_width)
        height = _value(self.style.get("height"), available_height)

        if self.measure_func and not self.children:
            _COUNTERS["measure"] += 1
            measured = self.measure_func(width, MeasureMode.Undefined, height, MeasureMode.Undefined)
            if isinstance(measured, dict):
                width = _value(measured.get("width"), width)
                height = _value(measured.get("height"), height)
            elif isinstance(measured, tuple) and len(measured) >= 2:
                width = _value(measured[0], width)
                height = _value(measured[1], height)

        if math.isnan(width):
            width = sum(_value(c.style.get("width"), 0.0) for c in self.children) if self._is_row() else max([0.0] + [_value(c.style.get("width"), 0.0) for c in self.children])
        if math.isnan(height):
            height = max([0.0] + [_value(c.style.get("height"), 0.0) for c in self.children]) if self._is_row() else sum(_value(c.style.get("height"), 0.0) for c in self.children)

        width = self._clamp(width, "minWidth", "maxWidth")
        height = self._clamp(height, "minHeight", "maxHeight")
        self.layout = {"left": left, "top": top, "width": width, "height": height}

        cursor_x = left
        cursor_y = top
        for child in self.children:
            child_width = _value(child.style.get("width"), width if not self._is_row() else math.nan)
            child_height = _value(child.style.get("height"), height if self._is_row() else math.nan)
            child._layout_tree(child_width, child_height, cursor_x, cursor_y)
            if self._is_row():
                cursor_x += child.getComputedWidth()
            else:
                cursor_y += child.getComputedHeight()

    def _is_row(self) -> bool:
        return self.style.get("flexDirection") in (FlexDirection.Row, FlexDirection.RowReverse)

    def _clamp(self, value: float, min_key: str, max_key: str) -> float:
        min_value = _value(self.style.get(min_key))
        max_value = _value(self.style.get(max_key))
        if not math.isnan(min_value):
            value = max(value, min_value)
        if not math.isnan(max_value):
            value = min(value, max_value)
        return value

    def getComputedLeft(self) -> float:
        return self.layout["left"]

    def getComputedTop(self) -> float:
        return self.layout["top"]

    def getComputedWidth(self) -> float:
        return self.layout["width"]

    def getComputedHeight(self) -> float:
        return self.layout["height"]

    def getComputedRight(self) -> float:
        return 0.0

    def getComputedBottom(self) -> float:
        return 0.0

    def getComputedLayout(self) -> dict[str, float]:
        return {
            **self.layout,
            "right": self.getComputedRight(),
            "bottom": self.getComputedBottom(),
        }

    def getComputedBorder(self, edge: int) -> float:
        return float(self.style["border"].get(edge, self.style["border"].get(Edge.All, 0.0)))

    def getComputedPadding(self, edge: int) -> float:
        return float(self.style["padding"].get(edge, self.style["padding"].get(Edge.All, 0.0)))

    def getComputedMargin(self, edge: int) -> float:
        return float(self.style["margin"].get(edge, self.style["margin"].get(Edge.All, 0.0)))

    def _set(self, key: str, value: Any) -> None:
        self.style[key] = value

    def setWidth(self, v: Any) -> None: self._set("width", v)
    def setWidthPercent(self, v: float) -> None: self._set("width", f"{v}%")
    def setWidthAuto(self) -> None: self._set("width", None)
    def setHeight(self, v: Any) -> None: self._set("height", v)
    def setHeightPercent(self, v: float) -> None: self._set("height", f"{v}%")
    def setHeightAuto(self) -> None: self._set("height", None)
    def setMinWidth(self, v: Any) -> None: self._set("minWidth", v)
    def setMinWidthPercent(self, v: float) -> None: self._set("minWidth", f"{v}%")
    def setMinHeight(self, v: Any) -> None: self._set("minHeight", v)
    def setMinHeightPercent(self, v: float) -> None: self._set("minHeight", f"{v}%")
    def setMaxWidth(self, v: Any) -> None: self._set("maxWidth", v)
    def setMaxWidthPercent(self, v: float) -> None: self._set("maxWidth", f"{v}%")
    def setMaxHeight(self, v: Any) -> None: self._set("maxHeight", v)
    def setMaxHeightPercent(self, v: float) -> None: self._set("maxHeight", f"{v}%")
    def setFlexDirection(self, v: int) -> None: self._set("flexDirection", v)
    def setFlexGrow(self, v: Any) -> None: self._set("flexGrow", _value(v, 0.0))
    def setFlexShrink(self, v: Any) -> None: self._set("flexShrink", _value(v, 0.0))
    def setFlex(self, v: Any) -> None: self.setFlexGrow(v)
    def setFlexBasis(self, v: Any) -> None: self._set("flexBasis", v)
    def setFlexBasisPercent(self, v: float) -> None: self._set("flexBasis", f"{v}%")
    def setFlexBasisAuto(self) -> None: self._set("flexBasis", None)
    def setFlexWrap(self, v: int) -> None: self._set("flexWrap", v)
    def setAlignItems(self, v: int) -> None: self._set("alignItems", v)
    def setAlignSelf(self, v: int) -> None: self._set("alignSelf", v)
    def setAlignContent(self, v: int) -> None: self._set("alignContent", v)
    def setJustifyContent(self, v: int) -> None: self._set("justifyContent", v)
    def setDisplay(self, v: int) -> None: self._set("display", v)
    def getDisplay(self) -> int: return int(self.style["display"])
    def setPositionType(self, v: int) -> None: self._set("positionType", v)
    def setOverflow(self, v: int) -> None: self._set("overflow", v)
    def setDirection(self, v: int) -> None: self._set("direction", v)
    def setBoxSizing(self, _: int) -> None: return None
    def setPosition(self, edge: int, v: Any) -> None: self.style["position"][edge] = v
    def setPositionPercent(self, edge: int, v: float) -> None: self.style["position"][edge] = f"{v}%"
    def setPositionAuto(self, edge: int) -> None: self.style["position"][edge] = None
    def setMargin(self, edge: int, v: Any) -> None: self.style["margin"][edge] = v
    def setMarginPercent(self, edge: int, v: float) -> None: self.style["margin"][edge] = f"{v}%"
    def setMarginAuto(self, edge: int) -> None: self.style["margin"][edge] = None
    def setPadding(self, edge: int, v: Any) -> None: self.style["padding"][edge] = _value(v, 0.0)
    def setPaddingPercent(self, edge: int, v: float) -> None: self.style["padding"][edge] = f"{v}%"
    def setBorder(self, edge: int, v: Any) -> None: self.style["border"][edge] = _value(v, 0.0)
    def setGap(self, gutter: int, v: Any) -> None: self.style["gap"][gutter] = v
    def setGapPercent(self, gutter: int, v: float) -> None: self.style["gap"][gutter] = f"{v}%"
    def getFlexDirection(self) -> int: return int(self.style["flexDirection"])
    def getJustifyContent(self) -> int: return int(self.style["justifyContent"])
    def getAlignItems(self) -> int: return int(self.style["alignItems"])
    def getAlignSelf(self) -> int: return int(self.style["alignSelf"])
    def getAlignContent(self) -> int: return int(self.style["alignContent"])
    def getFlexGrow(self) -> float: return float(self.style["flexGrow"])
    def getFlexShrink(self) -> float: return float(self.style["flexShrink"])
    def getFlexBasis(self) -> Any: return self.style["flexBasis"]
    def getFlexWrap(self) -> int: return int(self.style["flexWrap"])
    def getWidth(self) -> Any: return self.style["width"]
    def getHeight(self) -> Any: return self.style["height"]
    def getOverflow(self) -> int: return int(self.style["overflow"])
    def getPositionType(self) -> int: return int(self.style["positionType"])
    def getDirection(self) -> int: return int(self.style["direction"])
    def setDirtiedFunc(self, _: Any) -> None: return None
    def unsetDirtiedFunc(self) -> None: return None
    def setIsReferenceBaseline(self, v: bool) -> None: self._set("referenceBaseline", bool(v))
    def setAspectRatio(self, _: Any) -> None: return None
    def getAspectRatio(self) -> float: return math.nan
    def setAlwaysFormsContainingBlock(self, _: bool) -> None: return None


def getYogaCounters() -> dict[str, int]:
    return dict(_COUNTERS)


class _Config:
    def __init__(self) -> None:
        self.pointScaleFactor = 1
        self.errata = Errata.None_
        self.useWebDefaults = False

    def free(self) -> None: return None
    def setExperimentalFeatureEnabled(self, *_: Any) -> None: return None
    def setPointScaleFactor(self, factor: float) -> None: self.pointScaleFactor = factor
    def getErrata(self) -> int: return int(self.errata)
    def setErrata(self, errata: int) -> None: self.errata = errata
    def setUseWebDefaults(self, v: bool) -> None: self.useWebDefaults = bool(v)


YOGA_INSTANCE = SimpleNamespace(
    Align=Align,
    BoxSizing=BoxSizing,
    Dimension=Dimension,
    Direction=Direction,
    Display=Display,
    Edge=Edge,
    Errata=Errata,
    ExperimentalFeature=ExperimentalFeature,
    FlexDirection=FlexDirection,
    Gutter=Gutter,
    Justify=Justify,
    MeasureMode=MeasureMode,
    Overflow=Overflow,
    PositionType=PositionType,
    Unit=Unit,
    Wrap=Wrap,
    Config=SimpleNamespace(create=lambda: _Config(), destroy=lambda *_: None),
    Node=SimpleNamespace(
        create=Node.create,
        createDefault=Node.createDefault,
        createWithConfig=Node.createWithConfig,
        destroy=lambda *_: None,
    ),
)


async def loadYoga() -> Any:
    return YOGA_INSTANCE


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
    "Node",
    "Overflow",
    "PositionType",
    "Unit",
    "Wrap",
    "YOGA_INSTANCE",
    "getYogaCounters",
    "loadYoga",
]
