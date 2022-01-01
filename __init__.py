from __future__ import annotations
from dataclasses import dataclass
from random import shuffle
from typing import Optional, Tuple


Color: int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(1, 5)

Hex: int
HEXES = range(19)

TileType: int
TILE_TYPES = (DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE) = range(6)
TILES = [DESERT] + [HILLS] * 3 + [FOREST] * 4 + \
    [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4

ResourceType: int
RESOURCE_TYPES = (BRICK, LUMBER, ORE, GRAIN, WOOL) = range(1, 6)

HarborType: int
HARBOR_TYPES = (*_, ANY) = range(1, 7)
HARBORS = [ANY] * 4 + list(HARBOR_TYPES[1:])


HEX_COORDS = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4), (2, 4),
              (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]


def vertex_from_hex_coords(x: int, y: int) -> Tuple[int, int]:
    return 2 * x + abs(2 - y), y


@dataclass
class Building:
    is_city: bool
    color: Color


@dataclass
class Road:
    seg_length: int
    color: Color


class CatanBoard:
    def __init__(self, board_str: Optional[str] = None) -> None:
        if board_str is None:
            self._init_random()
        else:
            self._set_board_str(board_str)

    def _init_random(self) -> None:
        tiles = TILES[:]
        shuffle(tiles)

        self.robber = tiles.index(DESERT)

        self.tiles = [tiles[:3] + [None] * 2, tiles[3:7] + [None],
                      tiles[7:12], [None] + tiles[12:16], [None] * 2 + tiles[16:]]

        self.harbors = HARBORS[:]
        shuffle(self.harbors)

        self.vertices = [[None] * 11] * 6
        self.edges = ...
