from __future__ import annotations
from dataclasses import dataclass, field
from random import randint, shuffle
from typing import Dict, Generator, List, Optional, Set, Tuple


Color = int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(1, 5)

BuildingType: bool
BUILDING_TYPES = (CITY, SETTLEMENT) = [True, False]

HarborType = int
HARBOR_TYPES = (BRICK_H, LUMBER_H, ORE_H, GRAIN_H, WOOL_H, ANY_H) = range(1, 7)

TileType = int
TILE_TYPES = (DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE) = range(6)

ResourceType = int
RESOURCE_TYPES = (BRICK, LUMBER, ORE, GRAIN, WOOL) = range(1, 6)

DevelopmentCard = int
DEVELOPMENT_CARDS = (KNIGHT, ROAD_BUILDING, YEAR_OF_PLENTY,
                     MONOPOLY, VICTORY_POINT) = range(1, 6)

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
class Tile:

    tile_type: TileType
    vertices: Tuple[Vertex] = field(default_factory=list)
    has_robber: bool = False


@dataclass
class Vertex:

    building: Optional[Building] = None
    harbor_type: Optional[HarborType] = None


@dataclass
class Edge:

    road: Optional[Road] = None


@dataclass
class Player:

    resources: List[int] = field(default_factory=lambda: [0] * 5)
    development_cards: List[DevelopmentCard] = field(default_factory=list)
    cities_left: int = 4
    settlements_left: int = 5
    roads_left: int = 15
    harbor_types: Set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    victory_points: int = 0


class _CatanBoard:

    _BASE_TILE_TYPES = [DESERT] + [HILLS] * 3 + [FOREST] * \
        4 + [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4
    _BASE_HARBOR_TYPES = list(HARBOR_TYPES[:-1]) + [ANY_H] * 4

    _BASE_TOKEN_TO_TILE_COORDS = {2: (1,), 3: (3, 16), 4: (9, 13), 5: (0, 14), 6: (
        2, 15), 8: (4, 10), 9: (6, 12), 10: (5, 11), 11: (8, 17), 12: (7,)}

    _TILE_COORDS = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4), (
        2, 4), (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]

    _VERTEX_IDX_TO_HARBOR_IDX = {0: 0, 2: 1, 3: 1, 6: 2, 7: 2, 9: 3, 10: 3,
                                 12: 4, 13: 4, 16: 5, 17: 5, 19: 6, 20: 6, 22: 7, 23: 7, 26: 8, 27: 8, 29: 0}

    def __init__(self) -> None:

        self._init_random()

    def _init_random(self) -> None:

        harbor_types = _CatanBoard._BASE_HARBOR_TYPES[:]
        shuffle(harbor_types)

        self._vertices = [Vertex(harbor_type=harbor_types[_CatanBoard._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                                 if vertex_idx in _CatanBoard._VERTEX_IDX_TO_HARBOR_IDX else None) for vertex_idx in VERTEX_IDXS]
        self._vertex_matrix = _CatanBoard._get_vertex_matrix_from_vertices(
            self._vertices)

        self._edges = [Edge() for _ in EDGE_IDXS]
        self._edge_matrix = _CatanBoard._get_edge_matrix_from_edges(
            self._edges)

        tile_types = _CatanBoard._BASE_TILE_TYPES[:]
        shuffle(tile_types)

        self._tiles = [Tile(tile_type, _CatanBoard._get_vertices_from_tile_coords(self._vertex_matrix, tile_coords),
                            tile_type == DESERT) for tile_type, tile_coords in zip(tile_types, _CatanBoard._TILE_COORDS)]
        self._tile_matrix = _CatanBoard._get_tile_matrix_from_tiles(
            self._tiles)

        desert_idx = tile_types.index(DESERT)
        self._token_to_tile = {roll: self._tiles[tile_idx + 1 if tile_idx >= desert_idx else tile_idx]
                               for roll, tile_idx in _CatanBoard._BASE_TOKEN_TO_TILE_COORDS.items()}

    @staticmethod
    def _get_tile_matrix_from_tiles(tiles: List[Tile]) -> List[List[Optional[Tile]]]:

        return [[tiles[0], tiles[11], tiles[10], None, None],
                [tiles[1], tiles[12], tiles[17], tiles[9], None],
                [tiles[2], tiles[13], tiles[18], tiles[16], tiles[8]],
                [None, tiles[3], tiles[14], tiles[15], tiles[7]],
                [None, None, tiles[4], tiles[5], tiles[6]]]

    @staticmethod
    def _get_vertex_matrix_from_vertices(vertices: List[Vertex]) -> List[List[Optional[Vertex]]]:

        return [[None, None, vertices[0], vertices[29], vertices[28], vertices[27], vertices[26], vertices[25], vertices[24], None, None],
                [None, vertices[2], vertices[1], vertices[30], vertices[47],
                    vertices[46], vertices[45], vertices[44], vertices[23], None],
                [vertices[4], vertices[3], vertices[32], vertices[31], vertices[48], vertices[53],
                    vertices[52], vertices[43], vertices[42], vertices[21], vertices[20]],
                [vertices[5], vertices[6], vertices[33], vertices[34], vertices[49], vertices[50],
                    vertices[51], vertices[40], vertices[41], vertices[18], vertices[19]],
                [None, vertices[7], vertices[8], vertices[35], vertices[36], vertices[37],
                    vertices[38], vertices[39], vertices[16], vertices[17], None],
                [None, None, vertices[9], vertices[10], vertices[11], vertices[12], vertices[13], vertices[14], vertices[15], None, None]]

    @staticmethod
    def _get_edge_matrix_from_edges(edges: List[Edge]) -> List[List[Optional[Edge]]]:

        ...

    @staticmethod
    def _get_vertices_from_tile_coords(vertex_matrix: List[List[Optional[Vertex]]], tile_coords: Tuple[int, int]) -> List[Vertex]:

        return [vertex_matrix[i][j] for i, j in _CatanBoard._get_vertices_coords_from_tile_coords(*tile_coords)]

    @staticmethod
    def _get_vertices_coords_from_tile_coords(i: int, j: int) -> Generator[Tuple[int, int], None, None]:

        i_0, j_0 = i, 2 * j + (2 - i)

        for k in range(6):
            yield i_0 + k // 3, j_0 + k % 3

    @staticmethod
    def _get_edges_coords_from_vertices_coords(i: int, j: int) -> Generator[Tuple[int, int], None, None]:

        i_0, j_0 = 2 * i, j
        J = (j_0,) * 3 + (j_0 + 1,) * 2 + (j_0 + 2,)

        for k in range(6):

            i_k, j_k = i_0 + k % 3, J[k]

            if 0 <= i_k < 11 and 0 <= j_k < 11:

                yield i_k, j_k


class Catan(_CatanBoard):

    players: Dict[Color, Player]
    turns: List[Color]

    def __init__(self, colors: List[Color]) -> None:

        assert 2 <= len(
            colors) <= 4, f"Must have 2-4 players, got {len(colors)}"
        assert all(
            color in COLORS for color in colors), f"Must have valid colors, got {colors}"

        self.players = {color: Player() for color in colors}
        self.turns = colors

        super().__init__()

    def end_turn(self) -> None:

        self.turns = self.turns[1:] + self.turns[:1]

    def give_resource(self, color: Color, resource_type: ResourceType, amount: int) -> None:

        self.players[color].resources[resource_type - 1] += amount

    def move_robber(self, tile_idx: TileIdx) -> None:

        ...

    def roll_dice(self) -> Roll:

        return randint(1, 6) + randint(1, 6)

    @property
    def is_game_over(self) -> bool:

        return self.winner is not None

    @property
    def winner(self) -> Optional[Color]:

        for color, player in self.players.items():

            if player.victory_points >= 10:

                return color

        return None


catan = Catan([BLUE, ORANGE])
