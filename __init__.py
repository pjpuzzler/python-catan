from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from random import choices, randint, shuffle


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

HarborIdx = int
HARBOR_IDXS = range(9)

TileIdx = int
TILE_IDXS = range(19)

VertexIdx = int
VERTEX_IDXS = range(54)

EdgeIdx = int
EDGE_IDXS = range(72)

PlayerIdx = int
PLAYER_IDXS = range(4)

Token = int
TOKENS = [*range(2, 7), *range(8, 13)]

Roll = int
ROLLS = range(2, 13)

COLOR_CODES = [
    "\x1b[38;2;26;110;219m",
    "\x1b[38;2;219;126;26m",
    "\x1b[38;2;222;29;29m",
    "\x1b[38;2;255;255;255m",
]
HARBOR_TYPE_CHARS = [
    "\x1b[38;2;199;97;54mBrk\033[0m",
    "\x1b[38;2;99;70;52mLum\033[0m",
    "\x1b[38;2;84;84;84mOre\033[0m",
    "\x1b[38;2;235;218;40mGrn\033[0m",
    "\x1b[38;2;186;186;186mWol\033[0m",
    "\x1b[38;2;16;108;194m?\033[0m",
]
TILE_TYPE_CHARS = [
    "\x1b[38;2;219;202;123mDes\033[0m",
    "\x1b[38;2;217;124;30mHil\033[0m",
    "\x1b[38;2;25;120;22mFor\033[0m",
    "\x1b[38;2;150;150;150mMnt\033[0m",
    "\x1b[38;2;235;218;40mFld\033[0m",
    "\x1b[38;2;103;235;80mPas\033[0m",
]

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
    road: Road | None = None

    adj_edges: tuple[Edge] | None = None
    adj_vertices: tuple[Vertex] | None = None

    def __repr__(self) -> str:
        return f"Edge({self.road})"


@dataclass(eq=False)
class Player:
    color: Color

    resource_amounts: list[int] = field(default_factory=lambda: [0] * 5)
    development_cards: list[DevelopmentCard] = field(default_factory=list)
    settlements_left: int = 5
    cities_left: int = 4
    roads_left: int = 15
    harbor_types: set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    victory_points: int = 0

    def __eq__(self, other: Player) -> bool:
        return self is other

    def __repr__(self) -> str:
        return f"Player({self.color.name})"

    def resource_cards(self) -> str:
        return " ".join(
            f"{resource_type.name} x{amount}"
            for resource_type, amount in zip(ResourceType, self.resource_amounts)
            if amount > 0
        )


@dataclass
class Road:
    color: Color

    def __repr__(self) -> str:
        return f"Road({self.color.name})"


@dataclass(eq=False)
class Tile:
    tile_type: TileType
    has_robber: bool = False

    adj_vertices: tuple[Vertex] | None = None

    def __eq__(self, other: Tile) -> bool:
        return self is other

    def __repr__(self) -> str:
        return f"Tile({self.tile_type.name}" + (", R)" if self.has_robber else ")")


@dataclass(eq=False)
class Vertex:
    harbor_type: HarborType

    building: Building | None = None

    adj_edges: tuple[Edge] | None = None
    adj_tiles: tuple[Tile] | None = None
    adj_vertices: tuple[Vertex] | None = None

    def __eq__(self, other: Vertex) -> bool:
        return self is other

    def __repr__(self) -> str:
        return f"Vertex({self.building})"


class _CatanBoard:
    _BASE_TOKEN_TO_TILE_IDXS = [
        None,
        None,
        (11,),
        (9, 14),
        (3, 17),
        (0, 16),
        (10, 15),
        None,
        (2, 8),
        (6, 12),
        (1, 7),
        (4, 13),
        (5,),
    ]

    _COUNTER_CLOCKWISE_TILE_IDXS = [
        0,
        11,
        10,
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
        12,
        17,
        16,
        15,
        14,
        13,
        18,
    ]

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

    _VERTEX_IDX_TO_HARBOR_IDX = [
        0,
        None,
        1,
        1,
        None,
        None,
        2,
        2,
        None,
        3,
        3,
        None,
        4,
        4,
        None,
        None,
        5,
        5,
        None,
        6,
        6,
        None,
        7,
        7,
        None,
        None,
        8,
        8,
        None,
        0,
    ]

    def __init__(
        self,
        tile_types: list[TileType] | None = None,
        harbor_types: list[HarborType] | None = None,
    ) -> None:
        if tile_types is None:
            tile_types = BASE_TILE_TYPES[:]
            shuffle(tile_types)

        if harbor_types is None:
            harbor_types = BASE_HARBOR_TYPES[:]
            shuffle(harbor_types)

        self.edges = [Edge() for _ in EDGE_IDXS]
        self.tiles = [
            Tile(tile_type, has_robber=(tile_type is TileType.DESERT))
            for tile_type in tile_types
        ]
        self.vertices = [
            Vertex(
                harbor_type=harbor_types[self._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                if vertex_idx < len(self._VERTEX_IDX_TO_HARBOR_IDX)
                and self._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx] is not None
                else None
            )
            for vertex_idx in VERTEX_IDXS
        ]

        robber_tile_idx = tile_types.index(TileType.DESERT)
        self.robber_tile = self.tiles[robber_tile_idx]

        self.token_to_tiles = [None] * (max(TOKENS) + 1)
        for token in TOKENS:
            self.token_to_tiles[token] = tuple(
                self.tiles[
                    self._COUNTER_CLOCKWISE_TILE_IDXS[
                        self._COUNTER_CLOCKWISE_TILE_IDXS.index(tile_idx) + 1
                    ]
                    if self._COUNTER_CLOCKWISE_TILE_IDXS[tile_idx]
                    >= self._COUNTER_CLOCKWISE_TILE_IDXS[robber_tile_idx]
                    else tile_idx
                ]
                for tile_idx in self._BASE_TOKEN_TO_TILE_IDXS[token]
            )

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

    def _get_edge_char(self, edge_idx: EdgeIdx, default_char: str) -> str:
        edge = self.edges[edge_idx]
        return (
            f"{COLOR_CODES[edge.road.color.value]}{default_char}\033[0m"
            if edge.road is not None
            else f"\033[2m{default_char}\033[0m"
        )

    def _get_harbor_char(self, harbor_type: HarborType) -> str:
        return HARBOR_TYPE_CHARS[harbor_type.value]

    def _get_tile_char(self, tile_idx: TileIdx) -> str:
        tile = self.tiles[tile_idx]
        return TILE_TYPE_CHARS[tile.tile_type.value] + ("*" if tile.has_robber else " ")

    def _get_token_char(self, tile_idx: TileIdx) -> str:
        for token in TOKENS:
            if self.tiles[tile_idx] in self.token_to_tiles[token]:
                return f"({token}) ".rjust(5)
        return "     "

    def _get_vertex_char(self, vertex_idx: VertexIdx) -> str:
        vertex = self.vertices[vertex_idx]
        return (
            f"{COLOR_CODES[vertex.building.color.value]}{'X' if vertex.building.building_type is BuildingType.CITY else 'x'}\033[0m"
            if vertex.building is not None
            else "\033[2m.\033[0m"
        )

    def __str__(self) -> str:
        # fmt: off
        return ''.join(
            (
                '                        {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (0, 2, 4))),
                '\n',
                '\n',
                '\n',
                '                   {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((0, 1, 2, 3, 4, 5), ('/', '\\', '/', '\\', '/', '\\')))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (29, 1, 3, 5))),
                '\n',
                '\n',
                '                      {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (0, 1, 2))),
                '\n',
                '                {0}      {4}     {1}      {5}     {2}      {6}     {3}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((29, 30, 31, 6), ('|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (0, 1, 2))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (28, 30, 32, 6))),
                '\n',
                '\n',
                '\n',
                '           {}         {}     {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((28, 41, 42, 43, 44, 45, 32, 7), ('/', '\\', '/', '\\', '/', '\\', '/', '\\')))),
                '\n',
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (27, 47, 31, 33, 7))),
                '\n',
                '\n',
                '              {}           {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (11, 12, 13, 3))),
                '\n',
                '        {0}      {5}     {1}      {6}     {2}      {7}     {3}      {8}     {4}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((27, 59, 60, 46, 8), ('|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (11, 12, 13, 3))),
                '\n',
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
                '      {}           {}           {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (10, 17, 18, 14, 4))),
                '\n',
                '{0}      {6}     {1}      {7}     {2}      {8}     {3}      {9}     {4}      {10}     {5}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((25, 57, 71, 68, 48, 10), ('|', '|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (10, 17, 18, 14, 4))),
                '\n',
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
                '              {}           {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (9, 16, 15, 5))),
                '\n',
                '        {0}      {5}     {1}      {6}     {2}      {7}     {3}      {8}     {4}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((23, 55, 63, 50, 12), ('|', '|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (9, 16, 15, 5))),
                '\n',
                '\n',
                '\n',
                '        {}               {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (22, 42, 40, 38, 12))),
                '\n',
                '\n',
                '\n',
                '           {}         {}     {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((22, 38, 54, 53, 52, 51, 35, 13), ('\\', '/', '\\', '/', '\\', '/', '\\', '/')))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (21, 41, 39, 13))),
                '\n',
                '\n',
                '                      {}           {}           {}'.format(*(self._get_token_char(tile_idx) for tile_idx in (8, 7, 6))),
                '\n',
                '                {0}      {4}     {1}      {5}     {2}      {6}     {3}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((21, 37, 36, 14), ('|', '|', '|', '|'))), *(self._get_tile_char(tile_idx) for tile_idx in (8, 7, 6))),
                '\n',
                '\n',
                '\n',
                '                {}               {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (20, 18, 16, 14))),
                '\n',
                '\n',
                '\n',
                '                   {}         {}     {}         {}     {}         {}'.format(*(self._get_edge_char(edge_idx, default_char) for edge_idx, default_char in zip((20, 19, 18, 17, 16, 15), ('\\', '/', '\\', '/', '\\', '/')))),
                '\n',
                '\n',
                '\n',
                '                        {}               {}               {}'.format(*(self._get_vertex_char(vertex_idx) for vertex_idx in (19, 17, 15))),
            )
        )
        # fmt: on


class Catan(_CatanBoard):
    """
    Represents the game Catan.
    """

    development_cards: list[DevelopmentCard]
    edges: tuple[Edge]
    largest_army_player: Player | None
    longest_road_player: Player | None
    players: list[Player]
    resource_amounts: list[int]
    robber_tile: Tile
    tiles: tuple[Tile]
    token_to_tiles: list[tuple[Tile] | None]
    vertices: tuple[Vertex]

    def __init__(
        self,
        colors: list[Color],
        tile_types: list[TileType] | None = None,
        harbor_types: list[HarborType] | None = None,
    ) -> None:
        """
        Creates an instance of a Catan game.

        :param colors: The colors of the players (in the order of their turns).
        :param tile_types: The (optional) types of tiles to use (must have all tiles).
        :param harbor_types: The (optional) types of harbors to use (must have all harbors).
        """

        assert (
            2 <= len(colors) <= 4
        ), f"Number of colors must be 2-4, got {len(colors)}."
        assert len(set(colors)) == len(colors), "Colors must be unique."

        if tile_types is not None:
            assert len(tile_types) == len(BASE_TILE_TYPES) and all(
                tile_types.count(tile_type) == BASE_TILE_TYPES.count(tile_type)
                for tile_type in list(TileType)
            ), f"Tile types must have all tiles, got {tile_types}."

        if harbor_types is not None:
            assert len(harbor_types) == len(BASE_HARBOR_TYPES) and all(
                harbor_types.count(harbor_type) == BASE_HARBOR_TYPES.count(harbor_type)
                for harbor_type in list(HarborType)
            ), f"Harbor types must have all harbors, got {harbor_types}."

        super().__init__(tile_types, harbor_types)

        self.players = [Player(color) for color in colors]
        self._color_to_player = {player.color: player for player in self.players}
        self.resource_amounts = [19] * 5
        self.development_cards = [
            DevelopmentCard(development_card_type)
            for development_card_type in BASE_DEVELOPMENT_CARD_TYPES
        ]
        shuffle(self.development_cards)
        self.largest_army_player = None
        self.longest_road_player = None

    def _build_road(self, edge: Edge) -> None:
        player = self.turn

        player.roads_left -= 1

        edge.road = Road(player.color)

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
        player.longest_road = max(player.longest_road, longest_road)

        if player.longest_road >= 5 and (
            self.longest_road_player is None
            or self.longest_road_player is not player
            and player.longest_road > self.longest_road_player.longest_road
        ):
            if self.longest_road_player is not None:
                self.longest_road_player.victory_points -= 2

            self.longest_road_player = player

            player.victory_points += 2

    def _build_settlement(self, vertex: Vertex) -> None:
        player = self.turn

        player.settlements_left -= 1

        vertex.building = Building(player.color, BuildingType.SETTLEMENT)

        player.victory_points += 1

        if vertex.harbor_type is not None:
            player.harbor_types.add(vertex.harbor_type)

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

    def _modify_resources(
        self, player: Player, resource_amounts: dict[ResourceType, int]
    ) -> None:
        for resource_type, resource_amount in resource_amounts.items():
            player.resource_amounts[resource_type.value] += resource_amount

            self.resource_amounts[resource_type.value] -= resource_amount

    def build_road(self, edge_idx: EdgeIdx) -> None:
        """
        Builds a road.

        :param edge_idx: The index of the edge to build on.
        """

        player = self.turn

        assert player.roads_left > 0, "Player does not have any roads left."

        edge = self.edges[edge_idx]

        assert edge.road is None, "Edge must be unoccupied to build a road."

        assert any(
            adj_edge.road == Road(player.color) for adj_edge in edge.adj_edges
        ) or any(
            adj_vertex.building is not None
            and adj_vertex.building.color is player.color
            for adj_vertex in edge.adj_vertices
        ), "Edge must have an adjacent road, settlement, or city of the same color to build a road."

        assert all(
            player.resource_amounts[resource_type.value] >= abs(cost)
            for resource_type, cost in ROAD_COST.items()
        ), f"Player must have at least 1 lumber and 1 brick to build a road, has {player.resource_amounts[ResourceType.LUMBER.value]}l and {player.resource_amounts[ResourceType.BRICK.value]}b."

        self._modify_resources(player, ROAD_COST)

        self._build_road(edge)

    def build_settlement(self, vertex_idx: VertexIdx) -> None:
        """
        Builds a settlement.

        :param vertex_idx: The index of the vertex to build on.
        """

        player = self.turn

        assert player.settlements_left > 0, "Player does not have any settlements left."

        vertex = self.vertices[vertex_idx]

        assert (
            vertex.building is None
        ), "Vertex must be unoccupied to build a settlement."

        assert any(
            adj_edge.road == Road(player.color) for adj_edge in vertex.adj_edges
        ), "Vertex must have an adjacent road of the same color to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices
        ), "Vertex must have no adjacent buildings to build a settlement."

        assert all(
            player.resource_amounts[resource_type.value] >= abs(cost)
            for resource_type, cost in SETTLEMENT_COST.items()
        ), f"Player must have at least 1 lumber, 1 brick, 1 grain and 1 wool to build a settlement, has {player.resource_amounts[ResourceType.LUMBER.value]}l, {player.resource_amounts[ResourceType.BRICK.value]}b, {player.resource_amounts[ResourceType.GRAIN.value]}g and {player.resource_amounts[ResourceType.WOOL.value]}w."

        self._modify_resources(
            player,
            SETTLEMENT_COST,
        )

        self._build_settlement(vertex)

    def build_set_up_phase(
        self, vertex_idx: VertexIdx, edge_idx: EdgeIdx, round_two: bool = False
    ) -> None:
        """
        Builds a settlement and road in the set-up phase.

        :param vertex_idx: The index of the vertex to build the settlement on.
        :param edge_idx: The index of the edge to build the road on.
        :param round_two: Whether or not this is the second round of the set-up phase.
        """

        player = self.turn

        assert player.settlements_left > 0, "Player does not have any settlements left."

        vertex = self.vertices[vertex_idx]

        assert (
            vertex.building is None
        ), "Vertex must be unoccupied to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices
        ), "Vertex must have no adjacent buildings to build a settlement."

        assert player.roads_left > 0, "Player does not have any roads left."

        edge = self.edges[edge_idx]

        assert (
            edge in vertex.adj_edges
        ), "Road must be built adjacent to the settlement."

        assert edge.road is None, "Edge must be unoccupied to build a road."

        self._build_settlement(vertex)
        self._build_road(edge)

        if round_two:
            for adj_tile in vertex.adj_tiles:
                if adj_tile.tile_type != TileType.DESERT:
                    self._modify_resources(
                        player, {ResourceType(adj_tile.tile_type.value - 1): +1}
                    )

    def buy_development_card(self) -> None:
        """
        Buys a development card.
        """
        assert self.development_cards, "There are no development cards left."

        player = self.turn

        assert all(
            player.resource_amounts[resource_type.value] >= abs(cost)
            for resource_type, cost in DEVELOPMENT_CARD_COST.items()
        ), f"Player must have at least 1 grain, 1 wool, and 1 ore to buy a development card, has {player.resource_amounts[ResourceType.GRAIN.value]}g, {player.resource_amounts[ResourceType.WOOL.value]}w and {player.resource_amounts[ResourceType.ORE.value]}o."

        self._modify_resources(player, DEVELOPMENT_CARD_COST)

        development_card = self.development_cards.pop()
        player.development_cards.append(development_card)

        if development_card.development_card_type is DevelopmentCardType.VICTORY_POINT:
            player.victory_points += 1

    def discard_half(
        self, player: Player, resource_amounts: dict[ResourceType, int]
    ) -> None:
        """
        Discards half of a player's resources.

        :param player: The player to discard resources for.
        :param resource_amounts: The amounts of resources to discard.
        """

        assert all(
            player.resource_amounts[resource_type.value] >= amount
            for resource_type, amount in resource_amounts.items()
        ), "Player cannot discard more resources than they have."

        num_resources_discarded = sum(resource_amounts.values())
        num_player_resources = sum(player.resource_amounts)
        assert (
            num_resources_discarded == num_player_resources // 2
        ), f"Player must discard half of their total resources (rounded down), has {num_player_resources}, discarded {num_resources_discarded}."

        self._modify_resources(
            player,
            {
                resource_type: -amount
                for resource_type, amount in resource_amounts.items()
            },
        )

    def domestic_trade(
        self,
        resource_amounts_out: dict[ResourceType, int],
        resource_amounts_in: dict[ResourceType, int],
        color_to_trade_with: Color,
    ) -> None:
        """
        Trades resources between two players.

        :param resource_amounts_out: The amounts of resources the player is trading away.
        :param color_to_trade_with: The color of the player to trade with.
        :param resource_amounts_in: The amounts of resources the player is receiving.
        """

        player = self.turn

        assert color_to_trade_with in [
            other_player.color
            for other_player in self.players
            if other_player.color is not player.color
        ], "Player to trade with must be in the game."

        assert all(
            amount > 0 for amount in resource_amounts_out.values()
        ), f"Player 1's resource amounts must all be positive, got {resource_amounts_out}."
        assert all(
            amount > 0 for amount in resource_amounts_in.values()
        ), f"Player 2's resource amounts must all be positive, got {resource_amounts_in}."

        assert len(resource_amounts_out) > 0, "Player 1 must trade at least 1 resource."
        assert len(resource_amounts_in) > 0, "Player 2 must trade at least 1 resource."

        assert not any(
            resource_type in resource_amounts_in
            for resource_type in resource_amounts_out
        ), "Player cannot trade for the same resource they are trading away."

        player_to_trade_with = self._color_to_player[color_to_trade_with]

        assert all(
            player.resource_amounts[resource_type.value] >= amount
            for resource_type, amount in resource_amounts_out.items()
        ), f"Player does not have enough resources to trade away, {resource_amounts_out}."
        assert all(
            player_to_trade_with.resource_amounts[resource_type.value] >= amount
            for resource_type, amount in resource_amounts_in.items()
        ), f"Player to trade with does not have enough resources to trade, {resource_amounts_in}."

        self._modify_resources(
            player,
            {
                resource_type: resource_amounts_in.get(resource_type, 0)
                - resource_amounts_out.get(resource_type, 0)
                for resource_type in ResourceType
            },
        )
        self._modify_resources(
            player_to_trade_with,
            {
                resource_type: resource_amounts_out.get(resource_type, 0)
                - resource_amounts_in.get(resource_type, 0)
                for resource_type in ResourceType
            },
        )

    def end_turn(self) -> None:
        """
        Changes the turn to the next player.
        """

        for development_card in self.turn.development_cards:
            if (
                development_card.development_card_type
                != DevelopmentCardType.VICTORY_POINT
            ):
                development_card.playable = True

        self.players = self.players[1:] + self.players[:1]

    def maritime_trade(
        self,
        resource_type_out: ResourceType,
        resource_type_in: ResourceType,
    ) -> None:
        """
        Trades resources for a maritime trade.

        :param resource_type_out: The type of resource the player is trading out.
        :param resource_type_in: The type of resource the player is trading in.
        """

        assert (
            resource_type_out is not resource_type_in
        ), "Cannot trade the same resource."

        player = self.turn

        resource_amount = (
            2
            if HarborType(resource_type_out.value) in player.harbor_types
            else 3
            if HarborType.GENERIC in player.harbor_types
            else 4
        )

        player_resource_amount = player.resource_amounts[resource_type_out.value]
        assert (
            player_resource_amount >= resource_amount
        ), f"Player does not have enough resources to trade {resource_amount}, has {player_resource_amount}."

        self._modify_resources(
            player, {resource_type_out: -resource_amount, resource_type_in: +1}
        )

    def move_robber(
        self, new_robber_tile_idx: TileIdx, color_to_take_from: Color | None = None
    ) -> None:
        """
        Moves the robber.

        :param new_robber_tile_idx: The index of the tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from.
        """

        player = self.turn

        assert (
            color_to_take_from is None or color_to_take_from is not player.color
        ), "Player cannot take cards from themselves."

        new_robber_tile = self.tiles[new_robber_tile_idx]

        assert (
            new_robber_tile is not self.robber_tile
        ), "Robber must not be on the same tile."

        colors_on_tile = {
            adj_vertex.building.color
            for adj_vertex in new_robber_tile.adj_vertices
            if adj_vertex.building is not None
        }

        if color_to_take_from is not None:
            assert (
                color_to_take_from in colors_on_tile
            ), f"Player {color_to_take_from.name} does not have any buildilngs on the robber tile."

            player_to_take_from = self._color_to_player[color_to_take_from]

            assert any(
                player_to_take_from.resource_amounts
            ), f"{player_to_take_from} does not have any resources."

            resource_type_to_take = choices(
                list(ResourceType), player_to_take_from.resource_amounts
            )[0]

            self._modify_resources(player_to_take_from, {resource_type_to_take: -1})
            self._modify_resources(player, {resource_type_to_take: +1})

        else:
            assert not any(
                any(self._color_to_player[color].resource_amounts)
                for color in colors_on_tile
            ), "Must take cards from a player on the robber tile if possible."

        self.robber_tile.has_robber = False
        new_robber_tile.has_robber = True
        self.robber_tile = new_robber_tile

    def play_knight(
        self, new_robber_tile_idx: TileIdx, color_to_take_from: Color | None
    ) -> None:
        """
        Plays a knight development card.

        :param new_robber_tile_idx: The index of the tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from.
        """

        player = self.turn

        assert (
            DevelopmentCard(DevelopmentCardType.KNIGHT, True)
            in player.development_cards
        ), "Player must have a knight bought on a previous turn to play a knight."

        self.move_robber(new_robber_tile_idx, color_to_take_from)

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.KNIGHT, True)
        )

        player.knights_played += 1

        if player.knights_played >= 3 and (
            self.largest_army_player is None
            or self.largest_army_player is not player
            and player.knights_played > self.largest_army_player.knights_played
        ):
            if self.largest_army_player is not None:
                self.largest_army_player.victory_points -= 2

            self.largest_army_player = player

            player.victory_points += 2

    def play_monopoly(self, resource_type: ResourceType) -> None:
        """
        Plays a monopoly development card.

        :param resource_type: The type of resource to monopolize.
        """

        player = self.turn

        assert (
            DevelopmentCard(DevelopmentCardType.MONOPOLY, True)
            in player.development_cards
        ), "Player must have a monopoly bought on a previous turn to play a monopoly."

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.MONOPOLY, True)
        )

        total_resource_amount = 0

        for other_player in self.players:
            if other_player is not player:
                other_player_resource_amount = other_player.resource_amounts[
                    resource_type.value
                ]

                total_resource_amount += other_player_resource_amount

                self._modify_resources(
                    other_player, {resource_type: -other_player_resource_amount}
                )

        self._modify_resources(player, {resource_type: +total_resource_amount})

    def play_road_building(
        self, edge_idx_1: EdgeIdx, edge_idx_2: EdgeIdx | None
    ) -> None:
        """
        Plays a road building development card.

        :param edge_idx_1: The index of the first edge.
        :param edge_idx_2: The index of the second edge, or None if the player only has one road left.
        """

        player = self.turn

        assert (
            DevelopmentCard(DevelopmentCardType.ROAD_BUILDING, True)
            in player.development_cards
        ), "Player must have a road building bought on a previous turn to play a road building."

        edge_1 = self.edges[edge_idx_1]

        assert edge_1.road is None, "Edge 1 must be unoccupied to build a road."

        assert any(
            adj_edge.road == Road(player.color) for adj_edge in edge_1.adj_edges
        ) or any(
            adj_vertex.building is not None
            and adj_vertex.building.color is player.color
            for adj_vertex in edge_1.adj_vertices
        ), "Edge 1 must have an adjacent road, settlement, or city of the same color to build a road."

        if edge_idx_2 is not None:
            edge_2 = self.edges[edge_idx_2]

            assert edge_2.road is None, "Edge 2 must be unoccupied to build a road."

            assert any(
                adj_edge.road == Road(player.color) or adj_edge is edge_1
                for adj_edge in edge_2.adj_edges
            ) or any(
                adj_vertex.building is not None
                and adj_vertex.building.color is player.color
                for adj_vertex in edge_2.adj_vertices
            ), f"Edge 2 must have an adjacent road, settlement, or city of the same color to build a road."

        else:
            assert player.roads_left > 0, f"Player does not have any roads left."

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.ROAD_BUILDING, True)
        )

        self._build_road(edge_1)

        if edge_idx_2 is not None:
            self._build_road(edge_2)

    def play_year_of_plenty(
        self, resource_type_1: ResourceType, resource_type_2: ResourceType | None
    ) -> None:
        """
        Plays a year of plenty development card.

        :param resource_type_1: The type of resource to take.
        :param resource_type_2: The type of resource to take, or None if the bank only has one card left.
        """

        player = self.turn

        assert (
            DevelopmentCard(DevelopmentCardType.YEAR_OF_PLENTY, True)
            in player.development_cards
        ), "Player must have a year of plenty bought on a previous turn to play a year of plenty."

        assert (
            self.resource_amounts[resource_type_1.value] > 0
        ), "There are not enough cards to take."

        resource_amounts = {resource_type_1: 1}

        if resource_type_2 is not None:
            assert (
                self.resource_amounts[resource_type_2.value] > 0
            ), f"There are not enough cards to take."

            resource_amounts[resource_type_2] = (
                2 if resource_type_2 is resource_type_1 else 1
            )

        player.development_cards.remove(
            DevelopmentCard(DevelopmentCardType.YEAR_OF_PLENTY, True)
        )

        self._modify_resources(player, resource_amounts)

    def produce_resources(self, token: Token) -> None:
        """
        Gives resources to players based on the token.

        :param token: The token to produce resources for.
        """

        for tile in self.token_to_tiles[token]:
            if tile.has_robber:
                continue

            resource_type = ResourceType(tile.tile_type.value - 1)

            resource_amounts = {}

            for adj_vertex in tile.adj_vertices:
                if adj_vertex.building is not None:
                    building = adj_vertex.building

                    resource_amounts[building.color] = resource_amounts.get(
                        building.color, 0
                    ) + (1 if building.building_type is BuildingType.SETTLEMENT else 2)

            if self.resource_amounts[resource_type.value] < sum(
                resource_amounts.values()
            ):
                if (
                    self.resource_amounts[resource_type.value] > 0
                    and len(resource_amounts) == 1
                ):
                    color = tuple(resource_amounts)[0]
                    self._modify_resources(
                        self._color_to_player[color],
                        {resource_type: self.resource_amounts[resource_type.value]},
                    )

                else:
                    continue

            else:
                for color, amount in resource_amounts.items():
                    self._modify_resources(
                        self._color_to_player[color],
                        {resource_type: amount},
                    )

    def upgrade_settlement(self, vertex_idx: VertexIdx) -> None:
        player = self.turn

        assert player.cities_left > 0, "Player does not have any cities left."

        vertex = self.vertices[vertex_idx]

        assert vertex.building == Building(
            player.color
        ), "Vertex must have a settlement of the same color to upgrade settlement."

        assert all(
            player.resource_amounts[resource_type.value] >= abs(cost)
            for resource_type, cost in CITY_COST.items()
        ), f"Player must have at least 2 grain and 3 ore to upgrade settlement, has {player.resource_amounts[ResourceType.GRAIN.value]}g and {player.resource_amounts[ResourceType.ORE.value]}o."

        self._modify_resources(player, CITY_COST)

        player.settlements_left += 1
        player.cities_left -= 1

        vertex.building.building_type = BuildingType.CITY

        player.victory_points += 1

    @property
    def is_game_over(self) -> bool:
        """
        Gets whether the game is over.

        :return: Whether or not the game is over.
        """

        return self.winner is not None

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
            if player.victory_points >= 10:
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
    catan = Catan(
        [Color.BLUE, Color.RED],
        [
            TileType.FOREST,
            TileType.FIELDS,
            TileType.MOUNTAINS,
            TileType.HILLS,
            TileType.FIELDS,
            TileType.PASTURE,
            TileType.FOREST,
            TileType.PASTURE,
            TileType.FIELDS,
            TileType.HILLS,
            TileType.FOREST,
            TileType.PASTURE,
            TileType.MOUNTAINS,
            TileType.HILLS,
            TileType.FOREST,
            TileType.MOUNTAINS,
            TileType.PASTURE,
            TileType.DESERT,
            TileType.FIELDS,
        ],
        [
            HarborType.ORE,
            HarborType.GENERIC,
            HarborType.BRICK,
            HarborType.GENERIC,
            HarborType.GRAIN,
            HarborType.WOOL,
            HarborType.GENERIC,
            HarborType.LUMBER,
            HarborType.GENERIC,
        ],
    )
    catan.build_set_up_phase(0, 1)
    catan.end_turn()
    catan.players[0].resource_amounts = [4] * 5
    catan.players[1].resource_amounts = [4] * 5
    catan.move_robber(0, Color.BLUE)
    print()


if __name__ == "__main__":
    main()
