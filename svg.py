from __future__ import annotations
from typing import Optional
import xml.etree.ElementTree as ET

import catan


CORNER_VIEWBOX_SIZE = 100

BUILDINGS = {
    "settlement": """""",
    "city": """""",
}


class SvgWrapper(str):
    def _repr_svg_(self) -> SvgWrapper:
        return self


def _svg(viewbox: int, size: Optional[int]) -> ET.Element:
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "version": "1.2",
        "baseProfile": "tiny",
        "viewBox": f"0 0 {viewbox:d} {viewbox:d}",
    })

    if size is not None:
        svg.set("width", str(size))
        svg.set("height", str(size))

    return svg


def building(building: catan.Building, size: Optional[int] = None) -> str:
    """
    Renders the given :class:`catan.Building` as an SVG image.
    """
    svg = _svg(CORNER_VIEWBOX_SIZE, size)
    svg.append(ET.fromstring(BUILDINGS[building.type]))
