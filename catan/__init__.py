from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from random import choice, choices, randint, shuffle
from typing import Any, Iterator

STARTING_RESOURCE_AMOUNT = 19
WINNING_VICTORY_POINTS = 10


class Color(Enum):
    BLUE, ORANGE, RED, WHITE = range(4)


class BuildingType(Enum):
    SETTLEMENT, CITY = range(2)


class TileType(Enum):
    DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE = range(6)


BASE_TILE_TYPES = (
    [TileType.DESERT]
    + [TileType.HILLS] * 3
    + [TileType.FOREST] * 4
    + [TileType.MOUNTAINS] * 3
    + [TileType.FIELDS] * 4
    + [TileType.PASTURE] * 4
)


class HarborType(Enum):
    BRICK, LUMBER, ORE, GRAIN, WOOL, GENERIC = range(6)


BASE_HARBOR_TYPES = list(HarborType) + [HarborType.GENERIC] * 3


class ResourceType(Enum):
    BRICK, LUMBER, ORE, GRAIN, WOOL = range(5)


class DevelopmentCardType(Enum):
    KNIGHT, ROAD_BUILDING, YEAR_OF_PLENTY, MONOPOLY, VICTORY_POINT = range(5)


BASE_DEVELOPMENT_CARD_TYPES = (
    [DevelopmentCardType.KNIGHT] * 14
    + [DevelopmentCardType.ROAD_BUILDING] * 2
    + [DevelopmentCardType.YEAR_OF_PLENTY] * 2
    + [DevelopmentCardType.MONOPOLY] * 2
    + [DevelopmentCardType.VICTORY_POINT] * 5
)


class Action(Enum):
    (
        END_TURN,
        BUILD_SET_UP,
        PRODUCE_RESOURCES,
        DISCARD_HALF,
        MOVE_ROBBER,
        PLAY_DEVELOPMENT_CARD,
        TRADE_DOMESTIC,
        TRADE_MARITIME,
        BUILD_ROAD,
        BUILD_SETTLEMENT,
        BUILD_CITY,
        BUY_DEVELOPMENT_CARD,
    ) = range(12)


HarborIdx = int
HARBOR_IDXS = range(9)

TileIdx = int
TILE_IDXS = range(19)

CORNER_TILE_IDXS = TILE_IDXS[:12:2]

VertexIdx = int
VERTEX_IDXS = range(54)

EdgeIdx = int
EDGE_IDXS = range(72)

PlayerIdx = int
PLAYER_IDXS = range(4)

Token = int
TOKENS = [*range(2, 7), *range(8, 13)]

BASE_TOKENS = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11, None]

Roll = int
ROLLS = range(2, 13)

COLOR_CODES = {
    Color.BLUE: "\x1b[38;2;26;110;219m",
    Color.ORANGE: "\x1b[38;2;219;126;26m",
    Color.RED: "\x1b[38;2;222;29;29m",
    Color.WHITE: "\x1b[38;2;255;255;255m",
}
HARBOR_TYPE_CHARS = {
    HarborType.BRICK: "\x1b[38;2;199;97;54mB\033[0m",
    HarborType.LUMBER: "\x1b[38;2;99;70;52mL\033[0m",
    HarborType.ORE: "\x1b[38;2;84;84;84mO\033[0m",
    HarborType.GRAIN: "\x1b[38;2;235;218;40mG\033[0m",
    HarborType.WOOL: "\x1b[38;2;186;186;186mW\033[0m",
    HarborType.GENERIC: "\x1b[38;2;16;108;194m?\033[0m",
}
TILE_TYPE_CHARS = {
    TileType.DESERT: "\x1b[38;2;219;202;123mDes\033[0m",
    TileType.HILLS: "\x1b[38;2;217;124;30mHil\033[0m",
    TileType.FOREST: "\x1b[38;2;25;120;22mFor\033[0m",
    TileType.MOUNTAINS: "\x1b[38;2;150;150;150mMnt\033[0m",
    TileType.FIELDS: "\x1b[38;2;235;218;40mFld\033[0m",
    TileType.PASTURE: "\x1b[38;2;103;235;80mPas\033[0m",
}

ROAD_COST = {ResourceType.LUMBER: 1, ResourceType.BRICK: 1}
SETTLEMENT_COST = {
    ResourceType.LUMBER: 1,
    ResourceType.BRICK: 1,
    ResourceType.GRAIN: 1,
    ResourceType.WOOL: 1,
}
CITY_COST = {ResourceType.GRAIN: 2, ResourceType.ORE: 3}
DEVELOPMENT_CARD_COST = {
    ResourceType.GRAIN: 1,
    ResourceType.WOOL: 1,
    ResourceType.ORE: 1,
}


class BuildLocationError(Exception):
    """Raised when a player tries to build on an invalid location."""


class DevelopmentCardError(Exception):
    """Raised when a player tries to play an invalid or nonexistent development card."""


class InvalidResourcesError(Exception):
    """Raised when a player doesn't have enough resources to perform an action."""


class NotEnoughGameCardsError(Exception):
    """Raised when the game doesn't have enough cards to perform an action."""


class NotEnoughPiecesError(Exception):
    """Raised when a player doesn't have enough pieces to perform an action."""


class PhaseError(Exception):
    """Raised when a player tries to perform an action during the wrong phase."""


class RobberError(Exception):
    """Raised when a player fails to move the robber."""


@dataclass
class Building:
    color: Color
    building_type: BuildingType = BuildingType.SETTLEMENT

    def __repr__(self) -> str:
        return f"{self.building_type.name}({self.color.name})"


@dataclass
class DevelopmentCard:
    development_card_type: DevelopmentCardType

    playable: bool = False

    def __repr__(self) -> str:
        return f"DevelopmentCard({self.development_card_type.name})"


@dataclass(eq=False)
class Edge:
    idx: int
    road: Road | None = None

    adj_edges: tuple[Edge] | None = None
    adj_vertices: tuple[Vertex] | None = None

    def __repr__(self) -> str:
        return f"Edge({self.idx}, {self.road})"


@dataclass(eq=False)
class Player:
    color: Color

    resource_amounts: dict[ResourceType, int] = field(
        default_factory=lambda: dict.fromkeys(ResourceType, 0)
    )
    development_cards: list[DevelopmentCard] = field(default_factory=list)
    settlements_left: int = 5
    cities_left: int = 4
    roads_left: int = 15
    harbor_types: set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    victory_points: int = 0

    def __repr__(self) -> str:
        return f"Player({self.color.name})"


@dataclass
class Road:
    color: Color

    def __repr__(self) -> str:
        return f"Road({self.color.name})"


@dataclass(eq=False)
class Tile:
    idx: int
    tile_type: TileType
    has_robber: bool = False

    adj_vertices: tuple[Vertex] | None = None

    def __repr__(self) -> str:
        return f"Tile({self.idx}, {self.tile_type.name}" + (
            ", R)" if self.has_robber else ")"
        )


@dataclass(eq=False)
class Vertex:
    idx: int
    harbor_type: HarborType | None

    building: Building | None = None

    adj_edges: tuple[Edge] | None = None
    adj_tiles: tuple[Tile] | None = None
    adj_vertices: tuple[Vertex] | None = None

    def __repr__(self) -> str:
        return f"Vertex({self.idx}, {self.building})"


class _CatanBoard:
    _TILE_IDX_TO_ADJ_VERTEX_IDXS = [
        (0, 1, 30, 47, 28, 29),
        (2, 3, 32, 31, 30, 1),
        (4, 5, 6, 33, 32, 3),
        (6, 7, 8, 35, 34, 33),
        (8, 9, 10, 11, 36, 35),
        (36, 11, 12, 13, 38, 37),
        (38, 13, 14, 15, 16, 39),
        (40, 39, 16, 17, 18, 41),
        (42, 41, 18, 19, 20, 21),
        (44, 43, 42, 21, 22, 23),
        (26, 45, 44, 23, 24, 25),
        (28, 47, 46, 45, 26, 27),
        (30, 31, 48, 53, 46, 47),
        (32, 33, 34, 49, 48, 31),
        (34, 35, 36, 37, 50, 49),
        (50, 37, 38, 39, 40, 51),
        (52, 51, 40, 41, 42, 43),
        (46, 53, 52, 43, 44, 45),
        (48, 49, 50, 51, 52, 53),
    ]

    _VERTEX_IDX_TO_ADJ_EDGE_IDXS = [
        (0, 1),
        (1, 30, 2),
        (2, 3),
        (3, 31, 4),
        (4, 5),
        (5, 6),
        (6, 32, 7),
        (7, 8),
        (8, 33, 9),
        (9, 10),
        (10, 11),
        (11, 34, 12),
        (12, 13),
        (13, 35, 14),
        (14, 15),
        (15, 16),
        (16, 36, 17),
        (17, 18),
        (18, 37, 19),
        (19, 20),
        (20, 21),
        (21, 38, 22),
        (22, 23),
        (23, 39, 24),
        (24, 25),
        (25, 26),
        (26, 40, 27),
        (27, 28),
        (28, 41, 29),
        (29, 0),
        (42, 30, 43),
        (43, 44, 60),
        (44, 31, 45),
        (45, 32, 46),
        (61, 46, 47),
        (47, 33, 48),
        (49, 48, 34),
        (62, 49, 50),
        (51, 50, 35),
        (52, 51, 36),
        (53, 63, 52),
        (54, 53, 37),
        (38, 55, 54),
        (56, 55, 64),
        (57, 56, 39),
        (40, 58, 57),
        (59, 65, 58),
        (41, 42, 59),
        (66, 60, 67),
        (67, 61, 68),
        (68, 62, 69),
        (70, 69, 63),
        (71, 70, 64),
        (65, 66, 71),
    ]

    _VERTEX_IDX_TO_HARBOR_IDX = {
        0: 0,
        2: 1,
        3: 1,
        6: 2,
        7: 2,
        9: 3,
        10: 3,
        12: 4,
        13: 4,
        16: 5,
        17: 5,
        19: 6,
        20: 6,
        22: 7,
        23: 7,
        26: 8,
        27: 8,
        29: 0,
    }

    def __init__(
        self,
        *,
        tile_types: list[TileType] | None = None,
        tokens: list[Token | None] | None = None,
        harbor_types: list[HarborType] | None = None,
    ) -> None:
        if tile_types is None:
            tile_types = BASE_TILE_TYPES.copy()
            shuffle(tile_types)

        if harbor_types is None:
            harbor_types = BASE_HARBOR_TYPES.copy()
            shuffle(harbor_types)

        self._harbor_types = harbor_types

        self.edges = [Edge(edge_idx) for edge_idx in EDGE_IDXS]
        self.tiles = [
            Tile(tile_idx, tile_type, has_robber=(tile_type is TileType.DESERT))
            for tile_idx, tile_type in enumerate(tile_types)
        ]
        self.vertices = [
            Vertex(
                vertex_idx,
                harbor_type=harbor_types[self._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                if vertex_idx in self._VERTEX_IDX_TO_HARBOR_IDX
                else None,
            )
            for vertex_idx in VERTEX_IDXS
        ]

        for edge_idx, edge in enumerate(self.edges):
            adj_vertex_idxs = tuple(
                vertex_idx
                for vertex_idx in VERTEX_IDXS
                if edge_idx in self._VERTEX_IDX_TO_ADJ_EDGE_IDXS[vertex_idx]
            )

            edge.adj_vertices = tuple(
                self.vertices[adj_vertex_idx] for adj_vertex_idx in adj_vertex_idxs
            )
            edge.adj_edges = tuple(
                self.edges[adj_edge_idx]
                for adj_vertex_idx in adj_vertex_idxs
                for adj_edge_idx in self._VERTEX_IDX_TO_ADJ_EDGE_IDXS[adj_vertex_idx]
                if adj_edge_idx != edge_idx
            )

        for tile_idx, tile in enumerate(self.tiles):
            tile.adj_vertices = tuple(
                self.vertices[adj_vertex_idx]
                for adj_vertex_idx in self._TILE_IDX_TO_ADJ_VERTEX_IDXS[tile_idx]
            )

        for vertex_idx, vertex in enumerate(self.vertices):
            vertex.adj_edges = tuple(
                self.edges[adj_edge_idx]
                for adj_edge_idx in self._VERTEX_IDX_TO_ADJ_EDGE_IDXS[vertex_idx]
            )
            vertex.adj_tiles = tuple(
                self.tiles[tile_idx]
                for tile_idx in TILE_IDXS
                if vertex_idx in self._TILE_IDX_TO_ADJ_VERTEX_IDXS[tile_idx]
            )
            vertex.adj_vertices = tuple(
                self.vertices[other_vertex_idx]
                for adj_edge_idx in self._VERTEX_IDX_TO_ADJ_EDGE_IDXS[vertex_idx]
                for other_vertex_idx in VERTEX_IDXS
                if adj_edge_idx in self._VERTEX_IDX_TO_ADJ_EDGE_IDXS[other_vertex_idx]
                and other_vertex_idx != vertex_idx
            )

        desert_tile_idx = tile_types.index(TileType.DESERT)
        self.robber_tile = self.tiles[desert_tile_idx]

        if tokens is None:
            starting_tile_idx = choice(CORNER_TILE_IDXS)
            starting_offset = 12 - starting_tile_idx
            outer_layer = BASE_TOKENS[:12]
            inner_layer = BASE_TOKENS[12:-1]

            if desert_tile_idx < 12:
                outer_layer.insert(
                    (11 + (1 - desert_tile_idx) + starting_tile_idx) % 12, None
                )
                inner_layer.insert(0, outer_layer.pop())
            elif desert_tile_idx < 18:
                inner_layer.insert(
                    (5 + (13 - desert_tile_idx) + starting_tile_idx // 2) % 6, None
                )
            else:
                inner_layer.append(None)
            center = [inner_layer.pop()]

            outer_layer = (
                outer_layer[-starting_offset:] + outer_layer[:-starting_offset]
            )
            inner_layer = (
                inner_layer[-(starting_offset // 2) :]
                + inner_layer[: -(starting_offset // 2)]
            )

            outer_layer = outer_layer[:1] + outer_layer[:0:-1]
            inner_layer = inner_layer[:1] + inner_layer[:0:-1]

            tokens = outer_layer + inner_layer + center

        self.token_to_tiles = {
            token: tuple(
                self.tiles[tile_idx]
                for tile_idx in (i for i, t in enumerate(tokens) if t == token)
            )
            for token in TOKENS
        }
        self._tokens = tokens

    def _get_edge_char(self, edge_idx: EdgeIdx, default_char: str) -> str:
        edge = self.edges[edge_idx]
        return (
            f"{COLOR_CODES[edge.road.color]}{default_char}\033[0m"
            if edge.road is not None
            else f"\033[2m{default_char}\033[0m"
        )

    def _get_harbor_char(self, harbor_idx: HarborIdx) -> str:
        return HARBOR_TYPE_CHARS[self._harbor_types[harbor_idx]]

    def _get_tile_char(self, tile_idx: TileIdx) -> str:
        tile = self.tiles[tile_idx]
        return (
            ("\033[9m" if tile.has_robber else "")
            + TILE_TYPE_CHARS[tile.tile_type]
            + "\033[0m"
        )

    def _get_token_char(self, tile_idx: TileIdx) -> str:
        token = self._tokens[tile_idx]
        return "     " if token is None else f"({token}) ".rjust(5)

    def _get_vertex_char(self, vertex_idx: VertexIdx) -> str:
        vertex = self.vertices[vertex_idx]
        return (
            f"{COLOR_CODES[vertex.building.color]}{'X' if vertex.building.building_type is BuildingType.CITY else 'x'}\033[0m"
            if vertex.building is not None
            else "\033[2m.\033[0m"
        )

    def svg(self, *, show_indices: bool = False) -> str:
        """
        Returns an SVG representation of the board.
        """

        import catan.svg
        from IPython.display import SVG

        return SVG(catan.svg.board(self, show_indices))

    def __str__(self) -> str:
        # fmt: off
        return ''.join(
            (
                '                {0}   {2}   {4}               {5}   {3}   {1}       {6}'.format(*(self._get_harbor_char(harbor_idx) for harbor_idx in (0, 1)), '\x1b[38;2;158;158;158m_\033[0m', '\x1b[38;2;158;158;158m_\033[0m', *(self._get_vertex_char(vertex_idx) for vertex_idx in (0, 2, 4))),
                '\n',
                '\n',
                '\n',
                '                {0}  {2}         {3}     {4}         {5}  {1}  {6}         {7}'.format('\x1b[38;2;158;158;158m|\033[0m', '\x1b[38;2;158;158;158m|\033[0m', *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((0, 1, 2, 3, 4, 5), ('/', '\\', '/', '\\', '/', '\\')))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (29, 1, 3, 5))),
                '\n',
                '\n',
                '                      {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (0, 1, 2))),
                '\n',
                '                {0}      {4}      {1}      {5}      {2}      {6}      {3}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((29, 30, 31, 6), ('|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (0, 1, 2))),
                '\n',
                '\n',
                '\n',
                '                {2}               {3}               {4}               {5}   {1}   {0}'.format(self._get_harbor_char(2), '\x1b[38;2;158;158;158m_\033[0m', *(self._get_vertex_char(vertex_idx) for vertex_idx in (28, 30, 32, 6))),
                '\n',
                '\n',
                '\n',
                '           {1}         {2}     {3}         {4}     {5}         {6}     {7}         {8}  {0}'.format('\x1b[38;2;158;158;158m|\033[0m', *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((28, 41, 42, 43, 44, 45, 32, 7), ('/', '\\', '/', '\\', '/', '\\', '/', '\\')))),
                '\n',
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (27, 47, 31, 33, 7))),
                '\n',
                '\n',
                '     {}        {}           {}           {}           {}'.format('\x1b[38;2;158;158;158m/\033[0m', *(self._get_token_char(tile_idx) for tile_idx in (11, 12, 13, 3))),
                '\n',
                '    {0}   {1}      {6}      {2}      {7}      {3}      {8}      {4}      {9}      {5}'.format(self._get_harbor_char(8), *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((27, 59, 60, 46, 8), ('|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (11, 12, 13, 3))),
                '\n',
                '     {}'.format('\x1b[38;2;158;158;158m\\\033[0m'),
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (26, 46, 48, 34, 8))),
                '\n',
                '\n',
                '\n',
                '   {}         {}     {}         {}     {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((26, 40, 58, 65, 66, 67, 61, 47, 33, 9), ('/', '\\', '/', '\\', '/', '\\', '/', '\\', '/', '\\')))),
                '\n',
                '\n',
                '\n',
                '{}               {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (25, 45, 53, 49, 35, 9))),
                '\n',
                '\n',
                '      {1}           {2}           {3}           {4}           {5}        {0}'.format('\x1b[38;2;158;158;158m\\\033[0m', *(self._get_token_char(tile_idx) for tile_idx in (10, 17, 18, 14, 4))),
                '\n',
                '{1}      {7}      {2}      {8}      {3}      {9}      {4}      {10}      {5}      {11}      {6}   {0}'.format(self._get_harbor_char(3), *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((25, 57, 71, 68, 48, 10), ('|', '|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (10, 17, 18, 14, 4))),
                '\n',
                '                                                                                   {}'.format('\x1b[38;2;158;158;158m/\033[0m'),
                '\n',
                '\n',
                '{}               {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (24, 44, 52, 50, 36, 10))),
                '\n',
                '\n',
                '\n',
                '   {}         {}     {}         {}     {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((24, 39, 56, 64, 70, 69, 62, 49, 34, 11), ('\\', '/', '\\', '/', '\\', '/', '\\', '/', '\\', '/')))),
                '\n',
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (23, 43, 51, 37, 11))),
                '\n',
                '\n',
                '     {}        {}           {}           {}           {}'.format('\x1b[38;2;158;158;158m/\033[0m', *(self._get_token_char(tile_idx) for tile_idx in (9, 16, 15, 5))),
                '\n',
                '    {0}   {1}      {6}      {2}      {7}      {3}      {8}      {4}      {9}      {5}'.format(self._get_harbor_char(7), *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((23, 55, 63, 50, 12), ('|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (9, 16, 15, 5))),
                '\n',
                '     {}'.format('\x1b[38;2;158;158;158m\\\033[0m'),
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (22, 42, 40, 38, 12))),
                '\n',
                '\n',
                '\n',
                '           {1}         {2}     {3}         {4}     {5}         {6}     {7}         {8}  {0}'.format('\x1b[38;2;158;158;158m|\033[0m', *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((22, 38, 54, 53, 52, 51, 35, 13), ('\\', '/', '\\', '/', '\\', '/', '\\', '/')))),
                '\n',
                '\n',
                '\n',
                '                {2}               {3}               {4}               {5}   {1}   {0}'.format(self._get_harbor_char(4), '\x1b[38;2;158;158;158m_\033[0m', *(self._get_vertex_char(vertex_idx) for vertex_idx in (21, 41, 39, 13))),
                '\n',
                '\n',
                '                      {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (8, 7, 6))),
                '\n',
                '                {0}      {4}      {1}      {5}      {2}      {6}      {3}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((21, 37, 36, 14), ('|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (8, 7, 6))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (20, 18, 16, 14))),
                '\n',
                '\n',
                '\n',
                '                {0}  {2}         {3}     {4}         {5}  {1}  {6}         {7}'.format('\x1b[38;2;158;158;158m|\033[0m', '\x1b[38;2;158;158;158m|\033[0m', *(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((20, 19, 18, 17, 16, 15), ('\\', '/', '\\', '/', '\\', '/')))),
                '\n',
                '\n',
                '\n',
                '                {0}   {2}   {4}               {5}   {3}   {1}       {6}'.format(*(self._get_harbor_char(harbor_idx) for harbor_idx in (6, 5)), '\x1b[38;2;158;158;158m_\033[0m', '\x1b[38;2;158;158;158m_\033[0m', *(self._get_vertex_char(vertex_idx) for vertex_idx in (19, 17, 15))),
            )
        )
        # fmt: on

    def _repr_svg_(self) -> str:
        import catan.svg

        return catan.svg.board(self, False)


class Catan(_CatanBoard):
    """
    Represents the game Catan.
    """

    development_cards: list[DevelopmentCard]
    edges: tuple[Edge]
    largest_army_player: Player | None
    longest_road_player: Player | None
    players: list[Player]
    resource_amounts: dict[ResourceType, int]
    robber_tile: Tile
    tiles: tuple[Tile]
    token_to_tiles: dict[Token, tuple[Tile]]
    vertices: tuple[Vertex]

    def __init__(
        self,
        *,
        colors: list[Color] = list(Color),
        tile_types: list[TileType] | None = None,
        tokens: list[Token | None] | None = None,
        harbor_types: list[HarborType] | None = None,
        shuffle_order: bool = True,
    ) -> None:
        """
        Creates an instance of a Catan game.

        :param colors: The colors of the players (in the order of their turns).
        :param tile_types: The (optional) types of tiles to use (must have all tiles).
        :param tokens: The (optional) tokens to use (muse have all tokens).
        :param harbor_types: The (optional) types of harbors to use (must have all harbors).
        :param shuffle_order: Whether to randomize the order of play
        """

        if not (2 <= len(colors) <= 4):
            raise ValueError(f"Number of colors must be 2-4, got {len(colors)}.")
        if len(set(colors)) != len(colors):
            raise ValueError("Colors must be unique.")

        if (tile_types is None) != (tokens is None):
            raise ValueError(
                "Either both or neither of tile_types and tokens must be specified."
            )

        if tile_types is not None:
            if not (
                len(tile_types) == len(BASE_TILE_TYPES)
                and all(
                    tile_types.count(tile_type) == BASE_TILE_TYPES.count(tile_type)
                    for tile_type in TileType
                )
            ):
                raise ValueError(f"Tile types must have all tiles, got {tile_types}.")

        if tokens is not None:
            if not (
                len(tokens) == len(BASE_TOKENS)
                and all(
                    tokens.count(token) == BASE_TOKENS.count(token) for token in TOKENS
                )
            ):
                raise ValueError(f"Tokens must have all tokens, got {tokens}.")
            if tokens.index(None) != tile_types.index(TileType.DESERT):
                raise ValueError("Empty token must be on desert tile.")

        if harbor_types is not None:
            if not (
                len(harbor_types) == len(BASE_HARBOR_TYPES)
                and all(
                    harbor_types.count(harbor_type)
                    == BASE_HARBOR_TYPES.count(harbor_type)
                    for harbor_type in HarborType
                )
            ):
                raise ValueError(
                    f"Harbor types must have all harbors, got {harbor_types}."
                )

        super().__init__(
            tile_types=tile_types, tokens=tokens, harbor_types=harbor_types
        )

        if shuffle_order:
            shuffle(colors)
        self.players = [Player(color) for color in colors]
        self._color_to_player = {player.color: player for player in self.players}
        self.resource_amounts = dict.fromkeys(ResourceType, STARTING_RESOURCE_AMOUNT)
        self.development_cards = [
            DevelopmentCard(development_card_type)
            for development_card_type in BASE_DEVELOPMENT_CARD_TYPES
        ]
        shuffle(self.development_cards)
        self.largest_army_player = None
        self.longest_road_player = None
        self.round = 1
        self.turns_this_round = 0

        self._connected_edges = {color: set() for color in colors}
        self._connected_vertices = {color: set() for color in colors}
        self._distance_rule_vertices = set()
        self._building_vertices = {color: set() for color in colors}

        self._action_stack = []

    def __build_road(self, edge: Edge, *, save_state: bool = False) -> None:
        player = self.turn

        player.roads_left -= 1

        edge.road = Road(player.color)

        added_connected_edge_idxs, added_connected_vertex_idxs = [], []
        for adj_edge in edge.adj_edges:
            if adj_edge.idx not in self._connected_edges[player.color]:
                added_connected_edge_idxs.append(adj_edge.idx)
                self._connected_edges[player.color].add(adj_edge.idx)
        for adj_vertex in edge.adj_vertices:
            if adj_vertex.idx not in self._connected_vertices[player.color]:
                added_connected_vertex_idxs.append(adj_vertex.idx)
                self._connected_vertices[player.color].add(adj_vertex.idx)

        longest_road = 0
        stack = [edge]
        visited = set()
        while stack:
            cur_edge = stack.pop()
            longest_road = max(
                longest_road, self._get_longest_road_from_edge(cur_edge, None, set())
            )
            visited.add(cur_edge)
            for adj_edge in cur_edge.adj_edges:
                if adj_edge.road == Road(player.color) and adj_edge not in visited:
                    stack.append(adj_edge)
        prev_longest_road = player.longest_road
        player.longest_road = max(player.longest_road, longest_road)

        became_longest_road_player, prev_longest_road_player = False, None
        if player.longest_road >= 5 and (
            self.longest_road_player is None
            or self.longest_road_player is not player
            and player.longest_road > self.longest_road_player.longest_road
        ):
            became_longest_road_player, prev_longest_road_player = (
                True,
                self.longest_road_player,
            )

            if self.longest_road_player is not None:
                self.longest_road_player.victory_points -= 2

            self.longest_road_player = player

            player.victory_points += 2

        if save_state:
            self._action_stack[-1].append(
                [
                    edge,
                    added_connected_edge_idxs,
                    added_connected_vertex_idxs,
                    prev_longest_road,
                    became_longest_road_player,
                    prev_longest_road_player,
                ]
            )

    def __build_settlement(self, vertex: Vertex, *, save_state: bool = False) -> None:
        player = self.turn

        player.settlements_left -= 1

        vertex.building = Building(player.color)

        self._building_vertices[player.color].add(vertex.idx)

        added_distance_rule_vertex_idxs = []
        for adj_vertex in vertex.adj_vertices:
            if adj_vertex.idx not in self._distance_rule_vertices:
                added_distance_rule_vertex_idxs.append(adj_vertex.idx)
                self._distance_rule_vertices.add(adj_vertex.idx)

        player.victory_points += 1

        added_harbor_type = None
        if (
            vertex.harbor_type is not None
            and vertex.harbor_type not in player.harbor_types
        ):
            added_harbor_type = vertex.harbor_type
            player.harbor_types.add(vertex.harbor_type)

        if save_state:
            self._action_stack[-1].append(
                [
                    vertex,
                    added_distance_rule_vertex_idxs,
                    added_harbor_type,
                ]
            )

    def _build_city(self, vertex_idx: VertexIdx, *, save_state: bool = False) -> None:
        """
        Builds a city.

        :param vertex_idx: The index of the vertex to build on.

        :raises BuildLocationError:
        :raises InvalidResourcesError:
        :raises NotEnoughPiecesError:
        :raises ValueError:
        """

        if vertex_idx not in VERTEX_IDXS:
            raise ValueError(
                f"Vertex index must be in {VERTEX_IDXS}, got {vertex_idx}."
            )

        player = self.turn

        if player.cities_left == 0:
            raise NotEnoughPiecesError("Player has no cities left.")

        vertex = self.vertices[vertex_idx]

        if vertex.building != Building(player.color):
            raise BuildLocationError(
                f"Player does not have a settlement on vertex {vertex_idx}."
            )

        if not all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in CITY_COST.items()
        ):
            raise InvalidResourcesError(
                f"Player must have at least 2 grain and 3 ore to upgrade settlement, has {player.resource_amounts[ResourceType.GRAIN]}g and {player.resource_amounts[ResourceType.ORE]}o."
            )

        self._transfer_resources(player, None, CITY_COST)

        player.settlements_left += 1
        player.cities_left -= 1
        vertex.building.building_type = BuildingType.CITY
        player.victory_points += 1

        if save_state:
            self._action_stack[-1].append(vertex)

    def _build_road(self, edge_idx: EdgeIdx, *, save_state: bool = False) -> None:
        """
        Builds a road.

        :param edge_idx: The index of the edge to build on.

        :raises BuildLocationError:
        :raises InvalidResourcesError:
        :raises NotEnoughPiecesError:
        :raises ValueError:
        """

        if edge_idx not in EDGE_IDXS:
            raise ValueError(f"Edge index must be in {EDGE_IDXS}, got {edge_idx}.")

        player = self.turn

        if player.roads_left == 0:
            raise NotEnoughPiecesError("Player has no roads left.")

        edge = self.edges[edge_idx]

        if edge.road is not None:
            raise BuildLocationError(f"Edge {edge_idx} already has a road on it.")

        if not (
            any(adj_edge.road == Road(player.color) for adj_edge in edge.adj_edges)
            or any(
                adj_vertex.building.color is player.color
                for adj_vertex in edge.adj_vertices
                if adj_vertex.building is not None
            )
        ):
            raise BuildLocationError(
                f"Player must have a settlement or road adjacent to edge {edge_idx}."
            )

        if not all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in ROAD_COST.items()
        ):
            raise InvalidResourcesError(
                f"Player must have at least 1 lumber and 1 brick to build a road, has {player.resource_amounts[ResourceType.LUMBER]}l and {player.resource_amounts[ResourceType.BRICK]}b."
            )

        self._transfer_resources(player, None, ROAD_COST)

        self.__build_road(edge, save_state=save_state)

    def _build_set_up(
        self, vertex_idx: VertexIdx, edge_idx: EdgeIdx, *, save_state: bool = False
    ) -> None:
        """
        Builds a settlement and road in the set-up phase. Automatically ends the turn and distributes resources if necessary.

        :param vertex_idx: The index of the vertex to build the settlement on.
        :param edge_idx: The index of the edge to build the road on.

        :raises BuildLocationError:
        :raises PhaseError:
        :raises ValueError:
        """

        if vertex_idx not in VERTEX_IDXS:
            raise ValueError(
                f"Vertex index must be in {VERTEX_IDXS}, got {vertex_idx}."
            )
        if edge_idx not in EDGE_IDXS:
            raise ValueError(f"Edge index must be in {EDGE_IDXS}, got {edge_idx}.")

        if not self.is_set_up:
            raise PhaseError("Set-up phase is over.")

        player = self.turn

        vertex = self.vertices[vertex_idx]

        if vertex.building is not None:
            raise BuildLocationError(
                f"Vertex {vertex_idx} already has a building on it."
            )

        if not all(adj_vertex.building is None for adj_vertex in vertex.adj_vertices):
            raise BuildLocationError(
                f"Cannot have a settlement or city adjacent to vertex {vertex_idx}."
            )

        edge = self.edges[edge_idx]

        if edge.road is not None:
            raise BuildLocationError(f"Edge {edge_idx} already has a road on it.")

        if edge not in vertex.adj_edges:
            raise BuildLocationError(
                f"Edge {edge_idx} is not adjacent to vertex {vertex_idx}."
            )

        self.__build_settlement(vertex, save_state=save_state)
        self.__build_road(edge, save_state=save_state)

        second_round, resource_amounts = False, defaultdict(int)
        if self.round == 2:
            second_round = True
            for adj_tile in vertex.adj_tiles:
                if adj_tile.tile_type != TileType.DESERT:
                    resource_amounts[ResourceType(adj_tile.tile_type.value - 1)] += 1
        self._transfer_resources(None, player, resource_amounts)

        self._end_turn(save_state=save_state)

        if save_state:
            self._action_stack[-1].extend([second_round, resource_amounts])

    def _build_settlement(
        self, vertex_idx: VertexIdx, *, save_state: bool = False
    ) -> None:
        """
        Builds a settlement.

        :param vertex_idx: The index of the vertex to build on.

        :raises BuildLocationError:
        :raises InvalidResourcesError:
        :raises NotEnoughPiecesError:
        :raises ValueError:
        """

        if vertex_idx not in VERTEX_IDXS:
            raise ValueError(
                f"Vertex index must be in {VERTEX_IDXS}, got {vertex_idx}."
            )

        player = self.turn

        if player.settlements_left == 0:
            raise NotEnoughPiecesError("Player has no settlements left.")

        vertex = self.vertices[vertex_idx]

        if vertex.building is not None:
            raise BuildLocationError(
                f"Vertex {vertex_idx} already has a building on it."
            )

        if vertex_idx not in self._connected_vertices[player.color]:
            raise BuildLocationError(
                f"Player must have a road adjacent to vertex {vertex_idx}."
            )

        if vertex_idx in self._distance_rule_vertices:
            raise BuildLocationError(
                f"Cannot have a settlement or city adjacent to vertex {vertex_idx}."
            )

        if not all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in SETTLEMENT_COST.items()
        ):
            raise InvalidResourcesError(
                f"Player must have at least 1 lumber, 1 brick, 1 grain and 1 wool to build a settlement, has {player.resource_amounts[ResourceType.LUMBER]}l, {player.resource_amounts[ResourceType.BRICK]}b, {player.resource_amounts[ResourceType.GRAIN]}g and {player.resource_amounts[ResourceType.WOOL]}w."
            )

        self._transfer_resources(player, None, SETTLEMENT_COST)

        self.__build_settlement(vertex, save_state=save_state)

    def _buy_development_card(self, *, save_state: bool = False) -> None:
        """
        Buys a development card.

        :raises InvalidResourcesError:
        :raises NotEnoughGameCardsError:
        """

        if not self.development_cards:
            raise NotEnoughGameCardsError("No development cards left.")

        player = self.turn

        if not all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in DEVELOPMENT_CARD_COST.items()
        ):
            raise InvalidResourcesError(
                f"Player must have at least 1 grain, 1 wool, and 1 ore to buy a development card, has {player.resource_amounts[ResourceType.GRAIN]}g, {player.resource_amounts[ResourceType.WOOL]}w and {player.resource_amounts[ResourceType.ORE]}o."
            )

        self._transfer_resources(player, None, DEVELOPMENT_CARD_COST)

        development_card = self.development_cards.pop()
        player.development_cards.append(development_card)

        if development_card.development_card_type is DevelopmentCardType.VICTORY_POINT:
            player.victory_points += 1

        if save_state:
            self._action_stack[-1].append(development_card)

    def _discard_half(
        self,
        color: Color,
        amounts: list[int, int, int, int, int],
        *,
        save_state: bool = False,
    ) -> None:
        """
        Discards half of a player's resources.

        :param color: The color of the player to discard resources for.
        :param resource_amounts: The amounts of resources to discard.

        :raises ValueError
        """

        if color not in self._color_to_player:
            raise ValueError(f"Color must be in {self._color_to_player}, got {color}.")

        player = self._color_to_player[color]

        num_resources_discarded = sum(amounts)
        num_player_resources = sum(player.resource_amounts.values())
        if num_resources_discarded != num_player_resources // 2:
            raise ValueError(
                f"Player must discard half of their total resources (rounded down), has {num_player_resources}, discarded {num_resources_discarded}."
            )

        resource_amounts = dict(zip(ResourceType, amounts))

        if not all(
            player.resource_amounts[resource_type] >= resource_amount
            for resource_type, resource_amount in resource_amounts.items()
        ):
            raise ValueError(
                f"Player does not have enough resources to discard {resource_amounts}."
            )

        self._transfer_resources(player, None, resource_amounts)

        if save_state:
            self._action_stack[-1].extend([player, resource_amounts])

    def _domestic_trade(
        self,
        resource_amounts_out: dict[ResourceType, int],
        resource_amounts_in: dict[ResourceType, int],
        color_to_trade_with: Color,
    ) -> None:
        """
        Trades resources between two players.

        :param resource_amounts_out: The amounts of resources the player is trading away.
        :param resource_amounts_in: The amounts of resources the player is receiving.
        :param color_to_trade_with: The color of the player to trade with.

        :raises InvalidResourcesError:
        :raises ValueError:
        """

        if color_to_trade_with not in self._color_to_player:
            raise ValueError(f"Player {color_to_trade_with} does not exist.")

        player = self.turn

        if color_to_trade_with is player.color:
            raise ValueError(f"Player cannot trade with themselves.")

        if len(resource_amounts_out) <= 0:
            raise ValueError(f"Player 1 must trade at least 1 resource.")
        if len(resource_amounts_in) <= 0:
            raise ValueError(f"Player 2 must trade at least 1 resource.")

        if not all(amount > 0 for amount in resource_amounts_out.values()):
            raise ValueError(
                f"Player 1's resource amounts must all be positive, got {resource_amounts_out}."
            )
        if not all(amount > 0 for amount in resource_amounts_in.values()):
            raise ValueError(
                f"Player 2's resource amounts must all be positive, got {resource_amounts_in}."
            )

        if any(
            resource_type in resource_amounts_in
            for resource_type in resource_amounts_out
        ):
            raise ValueError(
                f"Player 1 cannot trade a resource they are receiving, got {resource_amounts_out} and {resource_amounts_in}."
            )

        player_to_trade_with = self._color_to_player[color_to_trade_with]

        if not all(
            player.resource_amounts[resource_type] >= resource_amount
            for resource_type, resource_amount in resource_amounts_out.items()
        ):
            raise InvalidResourcesError(
                f"Player does not have enough resources to trade away, got {resource_amounts_out}."
            )
        if not all(
            player_to_trade_with.resource_amounts[resource_type] >= resource_amount
            for resource_type, resource_amount in resource_amounts_in.items()
        ):
            raise InvalidResourcesError(
                f"Player to trade with does not have enough resources to trade, got {resource_amounts_in}."
            )

        self._transfer_resources(player_to_trade_with, player, resource_amounts_in)
        self._transfer_resources(player, player_to_trade_with, resource_amounts_out)

    def _end_turn(self, *, save_state: bool = False) -> None:
        """
        Ends the current player's turn.
        """

        turns_that_round, prev_round = self.turns_this_round, self.round
        self.turns_this_round += 1
        if self.turns_this_round == len(self.players):
            self.turns_this_round = 0
            self.round += 1

        unplayable_development_cards = []
        for development_card in self.turn.development_cards:
            if (
                development_card.development_card_type
                != DevelopmentCardType.VICTORY_POINT
                and not development_card.playable
            ):
                unplayable_development_cards.append(development_card)
                development_card.playable = True

        self.players = self.players[1:] + self.players[:1]

        flipped_order = False
        if self.turns_this_round == 0 and self.round in (2, 3):
            flipped_order = True
            self.players.reverse()

        if save_state:
            self._action_stack[-1].extend(
                [
                    turns_that_round,
                    prev_round,
                    unplayable_development_cards,
                    flipped_order,
                ]
            )

    def _get_longest_road_from_edge(
        self, edge: Edge, prev_edge: Edge | None, visited: set[Edge]
    ) -> int:
        player = self.turn

        visited.add(edge)

        valid_vertices = filter(
            lambda vertex: (prev_edge is None or vertex not in prev_edge.adj_vertices)
            and (vertex.building is None or vertex.building.color is player.color),
            edge.adj_vertices,
        )

        return 1 + max(
            (
                self._get_longest_road_from_edge(adj_edge, edge, visited)
                for vertex in valid_vertices
                for adj_edge in vertex.adj_edges
                if adj_edge.road == Road(player.color) and adj_edge not in visited
            ),
            default=0,
        )

    def _maritime_trade(
        self,
        resource_type_out: ResourceType,
        resource_type_in: ResourceType,
        *,
        save_state: bool = False,
    ) -> None:
        """
        Trades resources for a maritime trade.

        :param resource_type_out: The type of resource the player is trading out.
        :param resource_type_in: The type of resource the player is trading in.

        :raises InvalidResourcesError:
        :raises NotEnoughGameCardsError:
        :raises ValueError
        """

        if resource_type_out is resource_type_in:
            raise ValueError(f"Cannot trade {resource_type_out} for itself.")

        if self.resource_amounts[resource_type_in] == 0:
            raise NotEnoughGameCardsError(
                f"Not enough {resource_type_in} cards in the game."
            )

        player = self.turn

        resource_amount_out = (
            2
            if HarborType(resource_type_out.value) in player.harbor_types
            else 3
            if HarborType.GENERIC in player.harbor_types
            else 4
        )

        player_resource_amount = player.resource_amounts[resource_type_out]
        if player_resource_amount < resource_amount_out:
            raise InvalidResourcesError(
                f"Player does not have enough resources to trade {resource_amount_out}, has {player_resource_amount}."
            )

        resource_amounts_out, resource_amounts_in = {
            resource_type_out: resource_amount_out
        }, {resource_type_in: 1}
        self._transfer_resources(player, None, resource_amounts_out)
        self._transfer_resources(None, player, resource_amounts_in)

        if save_state:
            self._action_stack[-1].extend([resource_amounts_out, resource_amounts_in])

    def _move_robber(
        self,
        new_robber_tile_idx: TileIdx,
        color_to_take_from: Color | None = None,
        *,
        save_state: bool = False,
    ) -> None:
        """
        Moves the robber.

        :param new_robber_tile_idx: The index of the tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from or None if no valid options.

        :raises RobberError:
        :raises ValueError:
        """

        if new_robber_tile_idx not in TILE_IDXS:
            raise ValueError(f"Invalid tile index {new_robber_tile_idx}.")

        if (
            color_to_take_from is not None
            and color_to_take_from not in self._color_to_player
        ):
            raise ValueError(f"Invalid color {color_to_take_from}.")

        player = self.turn

        if color_to_take_from is not None and color_to_take_from is player.color:
            raise ValueError(f"Player cannot take from themselves.")

        new_robber_tile = self.tiles[new_robber_tile_idx]

        if new_robber_tile is self.robber_tile:
            raise RobberError(f"Robber is already on tile {new_robber_tile_idx}.")

        colors_on_tile = {
            adj_vertex.building.color
            for adj_vertex in new_robber_tile.adj_vertices
            if adj_vertex.building is not None
            and adj_vertex.building.color is not player.color
        }

        player_to_take_from, resource_type_take = None, None
        if color_to_take_from is not None:
            if color_to_take_from not in colors_on_tile:
                raise ValueError(
                    f"Player {color_to_take_from.name} does not have any buildilngs on the robber tile."
                )

            player_to_take_from = self._color_to_player[color_to_take_from]

            if any(amt > 0 for amt in player_to_take_from.resource_amounts.values()):
                resource_type_take = choices(
                    list(ResourceType),
                    player_to_take_from.resource_amounts.values(),
                )[0]
                self._transfer_resources(
                    player_to_take_from,
                    player,
                    {resource_type_take: 1},
                )
            else:
                player_to_take_from, resource_type_take = None, None

        else:
            if any(
                any(
                    amount > 0
                    for amount in self._color_to_player[color].resource_amounts.values()
                )
                for color in colors_on_tile
            ):
                raise ValueError(
                    "Must take cards from a player on the robber tile if possible."
                )

        if save_state:
            self._action_stack[-1].extend(
                [player_to_take_from, resource_type_take, self.robber_tile]
            )

        self.robber_tile.has_robber = False
        new_robber_tile.has_robber = True
        self.robber_tile = new_robber_tile

    def _play_knight(
        self,
        new_robber_tile_idx: TileIdx,
        color_to_take_from: Color | None = None,
        *,
        save_state: bool = False,
    ) -> None:
        """
        Plays a knight development card.

        :param new_robber_tile_idx: The index of the tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from or None if no valid options.

        :raises DevelopmentCardError:
        :raises RobberError:
        :raises ValueError:
        """

        player = self.turn

        if (
            DevelopmentCard(DevelopmentCardType.KNIGHT, True)
            not in player.development_cards
        ):
            raise DevelopmentCardError(
                "Player must have a knight bought on a previous turn to play a knight."
            )

        self._move_robber(
            new_robber_tile_idx, color_to_take_from, save_state=save_state
        )

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.KNIGHT, True)
        )

        player.knights_played += 1

        became_largest_army_player, prev_largest_army_player = False, None
        if player.knights_played >= 3 and (
            self.largest_army_player is None
            or self.largest_army_player is not player
            and player.knights_played > self.largest_army_player.knights_played
        ):
            became_largest_army_player, prev_largest_army_player = (
                True,
                self.largest_army_player,
            )
            if self.largest_army_player is not None:
                self.largest_army_player.victory_points -= 2

            self.largest_army_player = player

            player.victory_points += 2

        if save_state:
            self._action_stack[-1].extend(
                [became_largest_army_player, prev_largest_army_player]
            )

    def _play_monopoly(
        self, resource_type: ResourceType, *, save_state: bool = False
    ) -> None:
        """
        Plays a monopoly development card.

        :param resource_type: The type of resource to monopolize.

        :raises DevelopmentCardError:
        """

        player = self.turn

        if (
            DevelopmentCard(DevelopmentCardType.MONOPOLY, True)
            not in player.development_cards
        ):
            raise DevelopmentCardError(
                "Player must have a monopoly bought on a previous turn to play a monopoly."
            )

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.MONOPOLY, True)
        )

        transfers = []
        for other_player in self.players:
            if other_player is not player:
                resource_amounts = {
                    resource_type: other_player.resource_amounts[resource_type]
                }
                self._transfer_resources(
                    other_player,
                    player,
                    resource_amounts,
                )
                transfers.append((other_player, resource_amounts))

        if save_state:
            self._action_stack[-1].append(transfers)

    def _play_road_building(
        self,
        edge_idx_1: EdgeIdx,
        edge_idx_2: EdgeIdx | None = None,
        *,
        save_state: bool = False,
    ) -> None:
        """
        Plays a road building development card.

        :param edge_idx_1: The index of the first edge.
        :param edge_idx_2: The index of the second edge, or None if the player only has one road left.

        :raises BuildLocationError:
        :raises DevelopmentCardError:
        :raises NotEnoughPiecesError:
        :raises ValueError:
        """

        if edge_idx_1 not in EDGE_IDXS:
            raise ValueError(f"Invalid edge index {edge_idx_1}.")
        if edge_idx_2 is not None and edge_idx_2 not in EDGE_IDXS:
            raise ValueError(f"Invalid edge index {edge_idx_2}.")

        player = self.turn

        if (
            DevelopmentCard(DevelopmentCardType.ROAD_BUILDING, True)
            not in player.development_cards
        ):
            raise DevelopmentCardError(
                "Player must have a road building bought on a previous turn to play a road building."
            )

        if player.roads_left == 0:
            raise NotEnoughPiecesError("Player does not have any roads left.")
        if (edge_idx_2 is None) != (player.roads_left == 1):
            raise ValueError("Must use all roads.")

        edge_1 = self.edges[edge_idx_1]

        if edge_1.road is not None:
            raise BuildLocationError("Edge 1 must be unoccupied to build a road.")

        if not (
            any(adj_edge.road == Road(player.color) for adj_edge in edge_1.adj_edges)
            or any(
                adj_vertex.building is not None
                and adj_vertex.building.color is player.color
                for adj_vertex in edge_1.adj_vertices
            )
        ):
            raise BuildLocationError(
                "Edge 1 must have an adjacent road, settlement, or city of the same color to build a road."
            )

        if edge_idx_2 is not None:
            edge_2 = self.edges[edge_idx_2]

            if edge_2.road is not None:
                raise BuildLocationError("Edge 2 must be unoccupied to build a road.")

            if not (
                any(
                    adj_edge.road == Road(player.color) or adj_edge is edge_1
                    for adj_edge in edge_2.adj_edges
                )
                or any(
                    adj_vertex.building is not None
                    and adj_vertex.building.color is player.color
                    for adj_vertex in edge_2.adj_vertices
                )
            ):
                raise BuildLocationError(
                    "Edge 2 must have an adjacent road, settlement, or city of the same color to build a road."
                )

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.ROAD_BUILDING, True)
        )

        self.__build_road(edge_1, save_state=save_state)

        if edge_idx_2 is not None:
            self.__build_road(edge_2, save_state=save_state)

    def _play_year_of_plenty(
        self,
        resource_type_1: ResourceType,
        resource_type_2: ResourceType | None = None,
        *,
        save_state: bool = False,
    ) -> None:
        """
        Plays a year of plenty development card.

        :param resource_type_1: The type of the first resource to take.
        :param resource_type_2: The type of the second resource to take, or None if only one resource is taken.

        :raises DevelopmentCardError:
        :raises NotEnoughGameCardsError:
        :raises ValueError:
        """

        player = self.turn

        if (
            DevelopmentCard(DevelopmentCardType.YEAR_OF_PLENTY, True)
            not in player.development_cards
        ):
            raise DevelopmentCardError(
                "Player must have a year of plenty bought on a previous turn to play a year of plenty."
            )

        if (resource_type_2 is None) != (sum(self.resource_amounts.values()) == 1):
            raise ValueError(
                "Must only take one card when there is only one card left."
            )

        resource_amounts = defaultdict(int)

        resource_amounts[resource_type_1] += 1

        if resource_type_2 is not None:
            resource_amounts[resource_type_2] += 1

        if not all(
            self.resource_amounts[resource_type] >= amount
            for resource_type, amount in resource_amounts.items()
        ):
            raise NotEnoughGameCardsError("Must have enough resources in supply.")

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.YEAR_OF_PLENTY, True)
        )

        self._transfer_resources(None, player, resource_amounts)

        if save_state:
            self._action_stack[-1].append(resource_amounts)

    def _produce_resources(self, token: Token, *, save_state: bool = False) -> None:
        """
        Gives resources to players based on the token.

        :param token: The token to produce resources for.

        :raises ValueError:
        """

        if token not in TOKENS:
            raise ValueError("Token must be valid.")

        transfers = []
        for tile in self.token_to_tiles[token]:
            if tile.has_robber:
                continue

            color_amounts = defaultdict(int)
            resource_type = ResourceType(tile.tile_type.value - 1)

            for adj_vertex in tile.adj_vertices:
                building = adj_vertex.building
                if building is not None:
                    color_amounts[building.color] += (
                        2 if building.building_type is BuildingType.CITY else 1
                    )

            resource_amount_left = self.resource_amounts[resource_type]
            if (
                resource_amount_left < sum(color_amounts.values())
                and len(color_amounts) > 1
            ):
                continue

            else:
                for color, amount in color_amounts.items():
                    player, resource_amounts = self._color_to_player[color], {
                        resource_type: min(amount, resource_amount_left)
                    }
                    self._transfer_resources(
                        None,
                        player,
                        resource_amounts,
                    )
                    transfers.append((player, resource_amounts))

        if save_state:
            self._action_stack[-1].append(transfers)

    def _transfer_resources(
        self,
        player_from: Player | None,
        player_to: Player | None,
        resource_amounts: dict[ResourceType, int],
    ) -> None:
        if player_from is None:
            player_from = self
        elif player_to is None:
            player_to = self

        for resource_type, resource_amount in resource_amounts.items():
            player_from.resource_amounts[resource_type] -= resource_amount
            player_to.resource_amounts[resource_type] += resource_amount

    def _undo_end_turn(self, prev_states: list[Any]) -> None:
        (
            turns_that_round,
            prev_round,
            unplayable_development_cards,
            flipped_order,
        ) = prev_states

        if flipped_order:
            self.players.reverse()

        self.players = self.players[-1:] + self.players[:-1]

        for unplayable_development_card in unplayable_development_cards:
            unplayable_development_card.playable = False

        self.round = prev_round
        self.turns_this_round = turns_that_round

    def do_action(
        self, action: Action, extra: list[Any], *, save_state: bool = False
    ) -> None:
        """
        Does an action.

        :param action: The action to do.
        :param extra: The extra arguments for the action.
        :param save_state: Whether to save the state of the game before doing the action.
        """

        if self.is_set_up != (action is Action.BUILD_SET_UP):
            raise PhaseError(f"Cannot do action {action} in current phase.")

        if save_state:
            self._action_stack.append([action, extra])

        if action is Action.END_TURN:
            self._end_turn(save_state=save_state)
        elif action is Action.BUILD_SET_UP:
            vertex_idx, edge_idx = extra
            self._build_set_up(vertex_idx, edge_idx, save_state=save_state)
        elif action is Action.PRODUCE_RESOURCES:
            (token,) = extra
            self._produce_resources(token, save_state=save_state)
        elif action is Action.DISCARD_HALF:
            color, amounts = extra
            self._discard_half(color, amounts, save_state=save_state)
        elif action is Action.MOVE_ROBBER:
            new_robber_tile_idx, color_to_take_from = extra
            self._move_robber(
                new_robber_tile_idx, color_to_take_from, save_state=save_state
            )
        elif action is Action.PLAY_DEVELOPMENT_CARD:
            development_card_type, *extra = extra
            if development_card_type is DevelopmentCardType.KNIGHT:
                new_robber_tile_idx, color_to_take_from = extra
                self._play_knight(
                    new_robber_tile_idx, color_to_take_from, save_state=save_state
                )
            elif development_card_type is DevelopmentCardType.ROAD_BUILDING:
                edge_idx_1, edge_idx_2 = extra
                self._play_road_building(edge_idx_1, edge_idx_2, save_state=save_state)
            elif development_card_type is DevelopmentCardType.YEAR_OF_PLENTY:
                resource_type_1, resource_type_2 = extra
                self._play_year_of_plenty(
                    resource_type_1, resource_type_2, save_state=save_state
                )
            elif development_card_type is DevelopmentCardType.MONOPOLY:
                (resource_type,) = extra
                self._play_monopoly(resource_type, save_state=save_state)
        elif action is Action.TRADE_DOMESTIC:
            raise NotImplementedError
            amounts_out = [...]
            amounts_in = [...]
            resource_amounts_out = dict(zip(ResourceType, amounts_out))
            resource_amounts_in = dict(zip(ResourceType, amounts_in))

            for player in self.players[1:]:
                other_action = ...
                if other_action is Action.ACCEPT_TRADE:
                    color_to_trade_with = player.color
                    self.domestic_trade(
                        resource_amounts_out,
                        resource_amounts_in,
                        color_to_trade_with,
                    )
                    break
        elif action is Action.TRADE_MARITIME:
            resource_type_out, resource_type_in = extra
            self._maritime_trade(
                resource_type_out, resource_type_in, save_state=save_state
            )
        elif action is Action.BUILD_ROAD:
            (edge_idx,) = extra
            self._build_road(edge_idx, save_state=save_state)
        elif action is Action.BUILD_SETTLEMENT:
            (vertex_idx,) = extra
            self._build_settlement(vertex_idx, save_state=save_state)
        elif action is Action.BUILD_CITY:
            (vertex_idx,) = extra
            self._build_city(vertex_idx, save_state=save_state)
        elif action is Action.BUY_DEVELOPMENT_CARD:
            self._buy_development_card(save_state=save_state)

    def legal_discard_halfs(
        self, color: Color
    ) -> Iterator[list[int, int, int, int, int]]:
        player = self._color_to_player[color]
        amt_to_discard = sum(player.resource_amounts.values()) // 2

        def get_discard(
            cur: list[int, int, int, int, int],
            amts: dict[ResourceType, int],
            amt_left: int,
            resource_type: ResourceType,
        ) -> list[int, int, int, int, int]:
            if amt_left == 0:
                yield Action.DISCARD_HALF, color, cur
                return

            if resource_type == ResourceType.WOOL:
                if amts[resource_type] < amt_left:
                    return
                cur[resource_type.value] += amt_left
                yield Action.DISCARD_HALF, color, cur
                return

            for amt in range(min(amts[resource_type] + 1, amt_left + 1)):
                cur[resource_type.value] += amt
                amts[resource_type] -= amt
                yield from get_discard(
                    cur.copy(),
                    amts,
                    amt_left - amt,
                    ResourceType(resource_type.value + 1),
                )
                cur[resource_type.value] -= amt
                amts[resource_type] += amt

        yield from get_discard(
            [0] * 5, player.resource_amounts.copy(), amt_to_discard, ResourceType.BRICK
        )

    def undo_action(self) -> None:
        """
        Undoes the last action.
        """

        action, extra, *prev_states = self._action_stack.pop()

        if action is Action.END_TURN:
            self._undo_end_turn(prev_states=prev_states)
        elif action is Action.BUILD_SET_UP:
            (
                build_settlement_state,
                build_road_state,
                *prev_states,
                second_round,
                resource_amounts,
            ) = prev_states

            self._undo_end_turn(prev_states=prev_states)

            player = self.turn

            if second_round:
                self._transfer_resources(player, None, resource_amounts)

            (
                edge,
                added_connected_edge_idxs,
                added_connected_vertex_idxs,
                prev_longest_road,
                _,
                _,
            ) = build_road_state

            # if became_longest_road_player:
            #     player.victory_points -= 2

            #     self.longest_road_player = prev_longest_road_player

            #     if prev_longest_road_player is not None:
            #         prev_longest_road_player.victory_points += 2

            player.longest_road = prev_longest_road

            for edge_idx in added_connected_edge_idxs:
                self._connected_edges[player.color].remove(edge_idx)
            for vertex_idx in added_connected_vertex_idxs:
                self._connected_vertices[player.color].remove(vertex_idx)

            edge.road = None

            player.roads_left += 1

            (
                vertex,
                added_distance_rule_vertex_idxs,
                added_harbor_type,
            ) = build_settlement_state

            if added_harbor_type is not None:
                player.harbor_types.remove(added_harbor_type)

            player.victory_points -= 1

            for vertex_idx in added_distance_rule_vertex_idxs:
                self._distance_rule_vertices.remove(vertex_idx)

            self._building_vertices[player.color].remove(vertex.idx)

            vertex.building = None

            player.settlements_left += 1
        elif action is Action.PRODUCE_RESOURCES:
            (transfers,) = prev_states

            for player, resource_amounts in transfers:
                self._transfer_resources(player, None, resource_amounts)
        elif action is Action.DISCARD_HALF:
            player, resource_amounts = prev_states

            self._transfer_resources(None, player, resource_amounts)
        elif action is Action.MOVE_ROBBER:
            player = self.turn
            player_took_from, resource_type_took, prev_robber_tile = prev_states

            self.robber_tile.has_robber = False
            self.robber_tile = prev_robber_tile
            prev_robber_tile.has_robber = True

            if player_took_from is not None:
                self._transfer_resources(
                    player, player_took_from, {resource_type_took: 1}
                )
        elif action is Action.PLAY_DEVELOPMENT_CARD:
            player = self.turn
            development_card_type, *extra = extra
            if development_card_type is DevelopmentCardType.KNIGHT:
                (
                    player_took_from,
                    resource_type_took,
                    prev_robber_tile,
                    became_largest_army_player,
                    prev_largest_army_player,
                ) = prev_states

                if became_largest_army_player:
                    player.victory_points -= 2

                    self.largest_army_player = prev_largest_army_player

                    if prev_largest_army_player is not None:
                        prev_largest_army_player.victory_points += 2

                player.knights_played -= 1

                player.development_cards.append(
                    DevelopmentCard(DevelopmentCardType.KNIGHT, True)
                )

                self.robber_tile.has_robber = False
                self.robber_tile = prev_robber_tile
                prev_robber_tile.has_robber = True

                if player_took_from is not None:
                    self._transfer_resources(
                        player, player_took_from, {resource_type_took: 1}
                    )
            elif development_card_type is DevelopmentCardType.ROAD_BUILDING:
                build_road_states = prev_states

                for build_road_state in build_road_states[::-1]:
                    (
                        edge,
                        added_connected_edge_idxs,
                        added_connected_vertex_idxs,
                        prev_longest_road,
                        became_longest_road_player,
                        prev_longest_road_player,
                    ) = build_road_state

                    if became_longest_road_player:
                        player.victory_points -= 2

                        self.longest_road_player = prev_longest_road_player

                        if prev_longest_road_player is not None:
                            prev_longest_road_player.victory_points += 2

                    player.longest_road = prev_longest_road

                    for edge_idx in added_connected_edge_idxs:
                        self._connected_edges[player.color].remove(edge_idx)
                    for vertex_idx in added_connected_vertex_idxs:
                        self._connected_vertices[player.color].remove(vertex_idx)

                    edge.road = None

                    player.roads_left += 1

                player.development_cards.append(
                    DevelopmentCard(DevelopmentCardType.ROAD_BUILDING, True)
                )
            elif development_card_type is DevelopmentCardType.YEAR_OF_PLENTY:
                (resource_amounts,) = prev_states

                self._transfer_resources(player, None, resource_amounts)

                player.development_cards.append(
                    DevelopmentCard(DevelopmentCardType.YEAR_OF_PLENTY, True)
                )
            elif development_card_type is DevelopmentCardType.MONOPOLY:
                (transfers,) = prev_states

                for other_player, resource_amounts in transfers:
                    self._transfer_resources(player, other_player, resource_amounts)

                player.development_cards.append(
                    DevelopmentCard(DevelopmentCardType.MONOPOLY, True)
                )
        elif action is Action.TRADE_DOMESTIC:
            raise NotImplementedError
        elif action is Action.TRADE_MARITIME:
            player = self.turn
            resource_amounts_out, resource_amounts_in = prev_states

            self._transfer_resources(None, player, resource_amounts_out)
            self._transfer_resources(player, None, resource_amounts_in)
        elif action is Action.BUILD_ROAD:
            player = self.turn
            (build_road_state,) = prev_states

            (
                edge,
                added_connected_edge_idxs,
                added_connected_vertex_idxs,
                prev_longest_road,
                became_longest_road_player,
                prev_longest_road_player,
            ) = build_road_state

            if became_longest_road_player:
                player.victory_points -= 2

                self.longest_road_player = prev_longest_road_player

                if prev_longest_road_player is not None:
                    prev_longest_road_player.victory_points += 2

            player.longest_road = prev_longest_road

            for edge_idx in added_connected_edge_idxs:
                self._connected_edges[player.color].remove(edge_idx)
            for vertex_idx in added_connected_vertex_idxs:
                self._connected_vertices[player.color].remove(vertex_idx)

            edge.road = None

            player.roads_left += 1

            self._transfer_resources(None, player, ROAD_COST)
        elif action is Action.BUILD_SETTLEMENT:
            player = self.turn
            (build_settlement_state,) = prev_states

            (
                vertex,
                added_distance_rule_vertex_idxs,
                added_harbor_type,
            ) = build_settlement_state

            if added_harbor_type is not None:
                player.harbor_types.remove(added_harbor_type)

            player.victory_points -= 1

            for vertex_idx in added_distance_rule_vertex_idxs:
                self._distance_rule_vertices.remove(vertex_idx)

            self._building_vertices[player.color].remove(vertex.idx)

            vertex.building = None

            player.settlements_left += 1

            self._transfer_resources(None, player, SETTLEMENT_COST)
        elif action is Action.BUILD_CITY:
            player = self.turn
            (vertex,) = prev_states

            player.victory_points -= 1
            vertex.building.building_type = BuildingType.SETTLEMENT
            player.cities_left += 1
            player.settlements_left -= 1

            self._transfer_resources(None, player, CITY_COST)
        elif action is Action.BUY_DEVELOPMENT_CARD:
            player = self.turn
            (development_card,) = prev_states

            if (
                development_card.development_card_type
                is DevelopmentCardType.VICTORY_POINT
            ):
                player.victory_points -= 1

            player.development_cards.pop()
            self.development_cards.append(development_card)

            self._transfer_resources(None, player, DEVELOPMENT_CARD_COST)

    @property
    def is_game_over(self) -> bool:
        """
        Gets whether the game is over.

        :return: Whether or not the game is over.
        """

        return self.winner is not None

    @property
    def is_set_up(self) -> bool:
        """
        Gets whether the game is set up.

        :return: Whether or not the game is set up.
        """

        return self.round <= 2

    @property
    def legal_actions(self) -> Iterator[tuple[Action, ...]]:
        if self.is_set_up or self.is_game_over:
            return

        player = self.turn

        valid_edges = [
            edge_idx
            for edge_idx in EDGE_IDXS
            if self.edges[edge_idx].road is None
            and edge_idx in self._connected_edges[player.color]
        ]

        # build city
        if player.cities_left > 0 and all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in CITY_COST.items()
        ):
            for vertex_idx in VERTEX_IDXS:
                if self.vertices[vertex_idx].building != Building(player.color):
                    continue
                yield Action.BUILD_CITY, vertex_idx

        # build settlement
        if player.settlements_left > 0 and all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in SETTLEMENT_COST.items()
        ):
            for vertex_idx in VERTEX_IDXS:
                if (
                    self.vertices[vertex_idx].building is not None
                    or vertex_idx in self._distance_rule_vertices
                    or vertex_idx not in self._connected_vertices[player.color]
                ):
                    continue
                yield Action.BUILD_SETTLEMENT, vertex_idx

        # buy development card
        if self.development_cards and all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in DEVELOPMENT_CARD_COST.items()
        ):
            yield Action.BUY_DEVELOPMENT_CARD,

        # build road
        if player.roads_left > 0 and all(
            player.resource_amounts[resource_type] >= abs(cost)
            for resource_type, cost in ROAD_COST.items()
        ):
            for edge_idx in valid_edges:
                yield Action.BUILD_ROAD, edge_idx

        # play development card
        for development_card in player.development_cards:
            if not development_card.playable:
                continue

            if development_card.development_card_type is DevelopmentCardType.KNIGHT:
                for _, tile_idx, color_to_take_from in self.legal_robber_moves:
                    yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.KNIGHT, tile_idx, color_to_take_from
            elif (
                development_card.development_card_type
                is DevelopmentCardType.ROAD_BUILDING
            ):
                if player.roads_left == 0:
                    continue

                for edge_idx_1 in valid_edges:
                    if player.roads_left == 1:
                        yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.ROAD_BUILDING, edge_idx_1, None
                    else:
                        for edge_idx_2 in valid_edges:
                            if edge_idx_1 == edge_idx_2:
                                continue
                            yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.ROAD_BUILDING, edge_idx_1, edge_idx_2
            elif (
                development_card.development_card_type
                is DevelopmentCardType.YEAR_OF_PLENTY
            ):
                no_resources = True
                one_left_resource_type = None
                for resource_type, resource_amount in self.resource_amounts.items():
                    if resource_amount > 0:
                        no_resources = False
                        if one_left_resource_type is not None or resource_amount > 1:
                            one_left_resource_type = None
                            break
                        one_left_resource_type = resource_type

                if no_resources:
                    continue

                if one_left_resource_type is not None:
                    yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.YEAR_OF_PLENTY, one_left_resource_type, None
                    continue

                for resource_type_1 in ResourceType:
                    if self.resource_amounts[resource_type_1] == 0:
                        continue

                    for resource_type_2 in ResourceType:
                        if not (
                            self.resource_amounts[resource_type_2]
                            > (1 if resource_type_2 is resource_type_1 else 0)
                        ):
                            continue

                        yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.YEAR_OF_PLENTY, resource_type_1, resource_type_2
            elif development_card.development_card_type is DevelopmentCardType.MONOPOLY:
                for resource_type in ResourceType:
                    yield Action.PLAY_DEVELOPMENT_CARD, DevelopmentCardType.MONOPOLY, resource_type

        yield Action.END_TURN,

        # trade domestic
        # yield Action.TRADE_DOMESTIC

        # trade maritime
        for resource_type_out in ResourceType:
            resource_amount_out = (
                2
                if HarborType(resource_type_out.value) in player.harbor_types
                else 3
                if HarborType.GENERIC in player.harbor_types
                else 4
            )
            if player.resource_amounts[resource_type_out] < resource_amount_out:
                continue

            for resource_type_in in ResourceType:
                if (
                    resource_type_in is resource_type_out
                    or self.resource_amounts[resource_type_in] == 0
                ):
                    continue
                yield Action.TRADE_MARITIME, resource_type_out, resource_type_in

    @property
    def legal_set_ups(self) -> Iterator[tuple[VertexIdx, EdgeIdx]]:
        if not self.is_set_up:
            return

        for vertex_idx in VERTEX_IDXS:
            vertex = self.vertices[vertex_idx]
            if (
                vertex.building is not None
                or vertex_idx in self._distance_rule_vertices
            ):
                continue
            for edge in vertex.adj_edges:
                if edge.road is not None:
                    continue
                yield vertex_idx, edge.idx

    @property
    def legal_robber_moves(self) -> Iterator[tuple[Action, TileIdx, Color | None]]:
        player = self.turn
        for tile_idx in TILE_IDXS:
            if tile_idx == self.robber_tile.idx:
                continue
            tile = self.tiles[tile_idx]
            colors_on_tile = {
                adj_vertex.building.color
                for adj_vertex in tile.adj_vertices
                if adj_vertex.building is not None
                and adj_vertex.building.color is not player.color
            }
            if not colors_on_tile:
                yield Action.MOVE_ROBBER, tile_idx, None
            else:
                for color_to_take_from in colors_on_tile:
                    yield Action.MOVE_ROBBER, tile_idx, color_to_take_from

    @property
    def turn(self) -> Player:
        """
        Gets the player with the current turn.

        :return: The player who's current turn it is.
        """

        return self.players[0]

    @property
    def winner(self) -> Color | None:
        """
        Gets the winner of the game.

        :return: The color of the winner of the game, or None if there isn't one.
        """

        for player in self.players:
            if player.victory_points >= WINNING_VICTORY_POINTS:
                return player.color

        return None

    @staticmethod
    def roll_dice() -> Roll:
        """
        Rolls two six-sided dice.

        :return: The result of the dice roll.
        """

        return randint(1, 6) + randint(1, 6)


def main() -> None:
    """Example usage"""

    save_state = False
    c = Catan()

    while c.is_set_up:
        for player in c.players:
            vertex_idx, edge_idx = choice(list((c.legal_set_ups)))  # option
            c.do_action(
                Action.BUILD_SET_UP, [vertex_idx, edge_idx], save_state=save_state
            )

    while not c.is_game_over:
        roll = c.roll_dice()
        if roll == 7:
            for player in c.players:
                num_resources = sum(player.resource_amounts.values())
                if num_resources > 7:
                    action, *extra = choice(
                        list((c.legal_discard_halfs(player.color)))
                    )  # option
                    c.do_action(action, extra, save_state=save_state)

            action, *extra = choice(list((c.legal_robber_moves)))  # option
            c.do_action(action, extra, save_state=save_state)
        else:
            c.do_action(Action.PRODUCE_RESOURCES, [roll], save_state=save_state)

        while True:
            actions = list(c.legal_actions)
            action, *extra = choice(actions)  # option
            c.do_action(action, extra, save_state=save_state)
            if (
                action is Action.END_TURN
                or c.turn.victory_points >= WINNING_VICTORY_POINTS
            ):
                break

    print(c.winner)


if __name__ == "__main__":
    main()
