from __future__ import annotations
from typing import Optional, Tuple
import xml.etree.ElementTree as ET

import catan


HEX_HEIGHT = 100
# ratio of hexagon's height (vertex) to width (edge): [sqrt(3) : 2]
HEX_WIDTH = HEX_HEIGHT * 3 ** 0.5 / 2
CORNER_VIEWBOX_SIZE = 20

HEXES = {

}

BUILDINGS = {
    "bS": """""",
    "bC": """""",
    "oS": """""",
    "oC": """""",
    "rS": """""",
    "rC": """""",
    "wS": """""",
    "wC": """""",
}


class SvgWrapper(str):
    def _repr_svg_(self) -> SvgWrapper:
        return self


def _svg(viewbox: Tuple[int], size: Optional[int]) -> ET.Element:
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "version": "1.2",
        "baseProfile": "tiny",
        "viewBox": f"0 0 {viewbox[0]:d} {viewbox[1]:d}",
    })

    if size is not None:
        svg.set("width", str(size))
        svg.set("height", str(size))

    return svg


def building(building: catan.Building, size: Optional[int] = None) -> str:
    """
    Renders the given :class:`catan.Building` as an SVG image.
    """
    svg = _svg((CORNER_VIEWBOX_SIZE, CORNER_VIEWBOX_SIZE), size)
    svg.append(ET.fromstring(BUILDINGS[building.symbol()]))


def road(color: catan.Color, orientation: int, size: Optional[int] = None) -> str:
    """
    Renders the given :class:`catan.Road` as an SVG image.
    """
    raise NotImplementedError


def board(board: Optional[catan.BaseBoard] = None, *, size: Optional[int] = None) -> str:
    """
    Renders a board with buildings and roads as an SVG image.
    """
    svg = _svg((HEX_WIDTH, HEX_HEIGHT), size)

    defs = ET.SubElement(svg, "defs")
    if board:
        for building_color in catan.COLORS:
            for building_type in catan.BUILDING_TYPES:
                if board.buildings_mask(building_type, building_color):
                    defs.append(ET.fromstring(
                        BUILDINGS[catan.Building(building_type, building_color).symbol()]))

    # Render hexes and number tokens.
    for hex, bb in enumerate(catan.BB_HEXES):
        column_index = catan.hex_column(hex)
        row_index = catan.hex_row(hex)

        x = column_index * HEX_WIDTH
        y = row_index * HEX_HEIGHT

        if board.BB_HILLS & bb:
            href = "#hill"
        elif board.BB_FORESTS & bb:
            href = "#forest"
        elif board.BB_MOUNTAINS & bb:
            href = "#mountain"
        elif board.BB_FIELDS & bb:
            href = "#field"
        elif board.BB_PASTURES & bb:
            href = "#pasture"
        else:
            href = "#desert"

        ET.SubElement(svg, "use", {
            "href": href,
            "xlink:href": href,
            "transform": f"translate({x:d}, {y:d})",
        })

        for token in range(2, 13):
            if board.BB_TOKENS[token] & bb:
                ET.SubElement()
                break

    # Render buildings and roads.
    for hex, bb in enumerate(catan.BB_HEXES):
        pass
