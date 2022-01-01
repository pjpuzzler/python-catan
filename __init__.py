from __future__ import annotations

import enum
import typing

Color = int
COLORS = [BLUE, ORANGE, RED, WHITE] = range(1, 5)
COLOR_SYMBOLS = [None, "b", "o", "r", "w"]
COLOR_NAMES = [None, "blue", "orange", "red", "white"]

ResourceType = int
RESOURCE_TYPES = [BRICK, LUMBER, ORE, GRAIN, WOOL] = range(1, 6)
RESOURCE_SYMBOLS = [None, "b", "l", "o", "g", "w"]
RESOURCE_NAMES = [None, "brick", "lumber", "ore", "grain", "wool"]

HexType = int
HEX_TYPES = [DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE] = range(6)
HEX_SYMBOLS = ["d", "h", "f", "m", "i", "p"]
HEX_NAMES = ["desert", "hills", "forest", "mountains", "fields", "pasture"]

HarborType = int
HARBOR_TYPES = [ANY, *RESOURCE_TYPES] = range(6)
HARBOR_SYMBOLS = ["a"] + RESOURCE_SYMBOLS[1:]
HARBOR_NAMES = ["any"] + RESOURCE_NAMES[1:]

BuildingType = bool
BUILDING_TYPES = [CITY, SETTLEMENT] = [True, False]


def resource_symbol(resource_type: ResourceType) -> str:
    return typing.cast(str, RESOURCE_SYMBOLS[resource_type])


def resource_name(resource_type: ResourceType) -> str:
    return typing.cast(str, RESOURCE_NAMES[resource_type])


def hex_symbol(hex_type: HexType) -> str:
    return typing.cast(str, HEX_SYMBOLS[hex_type])


def hex_name(hex_type: HexType) -> str:
    return typing.cast(str, HEX_NAMES[hex_type])


def harbor_symbol(harbor_type: HarborType) -> str:
    return typing.cast(str, HARBOR_SYMBOLS[harbor_type])


def harbor_name(harbor_type: HarborType) -> str:
    return typing.cast(str, HARBOR_NAMES[harbor_type])


UNICODE_RESOURCE_SYMBOLS = {
    "b": "🧱",
    "l": "🪵",
    "o": "🪨",
    "g": "🌾",
    "w": "🐑",
}

UNICODE_HEX_SYMBOLS = {
    "d": "🏜",
    "h": "🧱",
    "f": "🪵",
    "m": "🪨",
    "i": "🌾",
    "p": "🐑",
}

UNICODE_HARBOR_SYMBOLS = dict({"a": "❓"}, **UNICODE_RESOURCE_SYMBOLS)

UNICODE_BUILDING_SYMBOLS = {
    "B": "🟦", "b": "🔵",
    "O": "🟧", "o": "🟠",
    "R": "🟥", "r": "🔴",
    "W": "⬜", "w": "⚪",
}

# hexes(top-left counterclockwise) harbors(top-left counterclockwise) vertices(top-top-left counterclockwise) edges(top-left counterclockwise) robber_hex color(order of turn):brick/lumber/ore/grain/wool/knights/road_buildings/year_of_plentys/monopolys/victory_point_cards/knights_played/road_buildings_played/year_of_plentys_played/monopolys_played/victory_point_cards_played longest_road_color largest_army_color
EXAMPLE_GAME_STRING = "miifhippmhfp/hfmifp/d albaawaog 30/r1w1r1b1o1b1w2o2/6 30/12/2w1r1b1o1b1w2o1r/6/6 19 b:1/1/1/0/0/0/0/0/0/0/0/0/0/0/0 o:0/0/1/2/0/0/0/0/0/0/0/0/0/0/0 r:0/2/0/1/0/0/0/0/0/0/0/0/0/0/0 w:1/1/0/1/0/0/0/0/0/0/0/0/0/0/0 - -"
"""The game string for the example starting position in the Catan booklet."""

EXAMPLE_BOARD_STRING = "miifhippmhfp/hfmifp/d albaawaog 30/r1w1r1b1o1b1w2o2/6 30/12/2w1r1b1o1b1w2o1r/6/6 19"
"""The board part of the game string for the example starting position in the Catan booklet."""


class Status(enum.IntFlag):
    VALID = 0
    BAD_HEXES = 1 << 0
    BAD_HARBORS = 1 << 1
    TOO_MANY_RESOURCES = 1 << 2
    TOO_MANY_DEVELOPMENT_CARDS = 1 << 3
    INVALID_LONGEST_ROAD = 1 << 4
    INVALID_LARGEST_ARMY = 1 << 5
    INVALID_BUILDINGS = 1 << 6
    INVALID_ROADS = 1 << 7


STATUS_VALID = Status.VALID
STATUS_BAD_HEXES = Status.BAD_HEXES
STATUS_BAD_HARBORS = Status.BAD_HARBORS
STATUS_TOO_MANY_RESOURCES = Status.TOO_MANY_RESOURCES
STATUS_TOO_MANY_DEVELOPMENT_CARDS = Status.TOO_MANY_DEVELOPMENT_CARDS
STATUS_INVALID_LONGEST_ROAD = Status.INVALID_LONGEST_ROAD
STATUS_INVALID_LARGEST_ARMY = Status.INVALID_LARGEST_ARMY
STATUS_INVALID_BUILDINGS = Status.INVALID_BUILDINGS
STATUS_INVALID_ROADS = Status.INVALID_ROADS

Hex = int
HEXES = range(19)

Vertex = int
VERTICES = range(54)

Edge = int
EDGES = range(72)

BB_EMPTY = 0

HexBitboard = int
HBB_ALL = 0x7_ffff

VertexBitboard = int
VBB_ALL = 0x3f_ffff_ffff_ffff

EdgeBitboard = int
EBB_ALL = 0xff_ffff_ffff_ffff_ffff
