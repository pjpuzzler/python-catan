from __future__ import annotations
from dataclasses import dataclass, field
from random import shuffle
from typing import Dict, List, Optional, Set, Tuple


Color = int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(1, 5)

BuildingType: bool
BUILDING_TYPES = (CITY, SETTLEMENT) = [True, False]

HarborType = int
HARBOR_TYPES = (BRICK, LUMBER, ORE, GRAIN, WOOL, ANY) = range(1, 7)

TileType = int
TILE_TYPES = (DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE) = range(6)

TileIdx = int
TILE_IDXS = range(19)

VertexIdx = int
VERTEX_IDXS = range(54)

EdgeIdx = int
EDGE_IDXS = range(72)

Roll = int


@dataclass
class Building:
    color: Color
    building_type: BuildingType = SETTLEMENT


@dataclass
class Road:
    color: Color
    longest_segment: int = 0


@dataclass
class Vertex:
    building: Optional[Building] = None
    harbor_type: Optional[HarborType] = None


@dataclass
class Tile:
    tile_type: TileType
    has_robber: bool = False


@dataclass
class Player:
    color: Color
    resources: List[int] = field(default_factory=lambda: [0] * 5)
    development_cards: List[int] = field(default_factory=lambda: [0] * 5)
    victory_points: int = 0
    harbor_types: Set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    cities_left: int = 4
    settlements_left: int = 5
    roads_left: int = 15


class CatanBoard:
    token_tiles: Dict[Roll, Tuple[TileIdx]]
    tiles: List[List[Optional[Tile]]]
    vertices: List[List[Optional[Vertex]]]
    edges: List[List[Optional[Road]]]

    BASE_TILE_TYPES = [DESERT] + [HILLS] * 3 + [FOREST] * \
        4 + [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4
    BASE_HARBOR_TYPES = list(HARBOR_TYPES[:-1]) + [ANY] * 4
    BASE_TOKEN_TILES = {2: (1,), 3: (3, 16), 4: (9, 13), 5: (0, 14), 6: (
        2, 15), 8: (4, 10), 9: (6, 12), 10: (5, 11), 11: (8, 17), 12: (7,)}

    HEX_COORDS = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4), (2, 4),
                  (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]
    HARBOR_COORDS = {(0, 2): 0, (0, 3): 0, (1, 1): 1, (2, 1): 1, (3, 1): 2, (4, 1): 2, (5, 2): 3, (5, 3): 3, (5, 5)                     : 4, (5, 6): 4, (4, 8): 5, (4, 9): 5, (2, 10): 6, (3, 10): 6, (1, 8): 7, (1, 9): 7, (0, 5): 8, (0, 6): 8}

    def __init__(self, board_str: Optional[str] = None) -> None:
        if board_str is None:
            self._init_random()
        else:
            self._init_board_str(board_str)

    def _init_random(self) -> None:
        base_tiles_types = CatanBoard.BASE_TILE_TYPES[:]
        shuffle(base_tiles_types)

        robber_idx = base_tiles_types.index(DESERT)
        self.token_tiles = {roll: tuple(tile_idx + 1 if tile_idx >= robber_idx else tile_idx for tile_idx in tile_idxs)
                            for roll, tile_idxs in CatanBoard.BASE_TOKEN_TILES.items()}

        self.tiles = [base_tiles_types[:3] + [None] * 2, base_tiles_types[3:7] + [None],
                      base_tiles_types[7:12], [None] + base_tiles_types[12:16], [None] * 2 + base_tiles_types[16:]]

        base_harbor_types = CatanBoard.BASE_HARBOR_TYPES[:]
        shuffle(base_harbor_types)

        self.vertices = [[None] * 11] * 6

        for i_t in range(5):
            for j_t in range(5):
                if self.tiles[i_t][j_t] is not None:
                    for i_v, j_v in CatanBoard._tile_to_vertices(i_t, j_t):
                        if self.vertices[i_v][j_v] is None:
                            self.vertices[i_v][j_v] = Vertex()
                            if (i_t, j_t) in CatanBoard.HARBOR_COORDS:
                                self.vertices[i_v][j_v].harbor_type = base_harbor_types[CatanBoard.HARBOR_COORDS[i_t, j_t]]

        self.edges = [[None] * 11] * 11

    def _init_board_str(self, board_str: str) -> None:
        raise NotImplementedError

    @staticmethod
    def _tile_to_vertices(i: int, j: int) -> List[Tuple[int, int]]:
        i_0, j_0 = i, 2 * j + (2 - i)
        return [(i_0 + k // 3, j_0 + k % 3) for k in range(6)]

    @staticmethod
    def _vertex_to_edges(i: int, j: int) -> List[Tuple[int, int]]:
        i_0, j_0 = 2 * i, j
        J = (j_0,) * 3 + (j_0 + 1,) * 2 + (j_0 + 2,)
        edges = []
        for k in range(6):
            i_k, j_k = i_0 + k % 3, J[k]
            if not (0 <= i_k < 11 and 0 <= j_k < 11):
                continue
            edges.append((i_k, j_k))
        return edges
