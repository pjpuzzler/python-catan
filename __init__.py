from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from random import randint, shuffle
from typing import Generator, Iterable


Color = int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(4)

BuildingType: bool
BUILDING_TYPES = (CITY, SETTLEMENT) = [True, False]

HarborType = int
HARBOR_TYPES = (BRICK_H, LUMBER_H, ORE_H, GRAIN_H, WOOL_H, ANY_H) = range(6)

TileType = int
TILE_TYPES = (DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE) = range(6)

ResourceType = int
RESOURCE_TYPES = (BRICK, LUMBER, ORE, GRAIN, WOOL) = range(5)

DevelopmentCard = int
DEVELOPMENT_CARDS = (KNIGHT, ROAD_BUILDING, YEAR_OF_PLENTY,
                     MONOPOLY, VICTORY_POINT) = range(5)

HarborIdx = int
HARBOR_IDXS = range(9)

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


@dataclass
class Tile:

    tile_type: TileType
    vertices: tuple[Vertex] = field(default_factory=list)
    has_robber: bool = False


@dataclass
class Vertex:

    building: Building | None = None
    harbor_type: HarborType | None = None
    longest_road: int = 0


@dataclass
class Edge:

    road: Road | None = None


@dataclass
class Player:

    resources: list[int] = field(default_factory=lambda: [0] * 5)
    development_cards: list[DevelopmentCard] = field(default_factory=list)
    buildings_left: list[int] = field(default_factory=lambda: [5, 4])
    roads_left: int = 15
    harbor_types: set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    victory_points: int = 0


class _CatanBoard:

    _BASE_HARBOR_TYPES: list[HarborType] = list(
        HARBOR_TYPES[:-1]) + [ANY_H] * 4
    _BASE_TILE_TYPES: list[TileType] = [DESERT] + [HILLS] * 3 + \
        [FOREST] * 4 + [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4

    _BASE_TOKEN_TO_TILE_IDXS: dict[Roll, tuple[TileIdx]] = {2: (1,), 3: (3, 16), 4: (9, 13), 5: (0, 14), 6: (
        2, 15), 8: (4, 10), 9: (6, 12), 10: (5, 11), 11: (8, 17), 12: (7,)}

    _EDGE_COORDS: list[tuple[int, int]] = []  # TODO

    _TILE_COORDS: list[tuple[int, int]] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (
        3, 4), (2, 4), (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]

    _VERTEX_COORDS: list[tuple[int, int]] = [(0, 2), (1, 2), (1, 1), (2, 1), (2, 0), (3, 0), (3, 1), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (4, 8), (4, 9), (3, 9), (3, 10), (2, 10), (2, 9), (1, 9), (1, 8), (
        0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (2, 3), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (3, 7), (3, 8), (2, 8), (2, 7), (1, 7), (1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (2, 6), (2, 5)]

    _VERTEX_IDX_TO_HARBOR_IDX: dict[VertexIdx, HarborIdx] = {
        0: 0, 2: 1, 3: 1, 6: 2, 7: 2, 9: 3, 10: 3, 12: 4, 13: 4, 16: 5, 17: 5, 19: 6, 20: 6, 22: 7, 23: 7, 26: 8, 27: 8, 29: 0}

    _vertex_matrix: list[list[Vertex | None]]
    _vertices: list[Vertex]

    def __init__(self) -> None:

        self._init_random()

    def _init_random(self) -> None:

        harbor_types = _CatanBoard._BASE_HARBOR_TYPES[:]
        shuffle(harbor_types)

        self._vertices = [Vertex(harbor_type=harbor_types[_CatanBoard._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                                 if vertex_idx in _CatanBoard._VERTEX_IDX_TO_HARBOR_IDX else None) for vertex_idx in VERTEX_IDXS]
        self._vertex_matrix = self._get_vertex_matrix()

        self._edges = [Edge() for _ in EDGE_IDXS]
        self._edge_matrix = self._get_edge_matrix()

        tile_types = _CatanBoard._BASE_TILE_TYPES[:]
        shuffle(tile_types)

        self._tiles = [Tile(tile_type, self._get_vertices_from_tile_coords(tile_coords), tile_type == DESERT)
                       for tile_type, tile_coords in zip(tile_types, _CatanBoard._TILE_COORDS)]
        self._tile_matrix = self._get_tile_matrix()

        desert_idx = tile_types.index(DESERT)
        self._token_to_tile = {roll: tuple(self._tiles[tile_idx + 1 if tile_idx >= desert_idx else tile_idx]
                                           for tile_idx in tile_idxs) for roll, tile_idxs in _CatanBoard._BASE_TOKEN_TO_TILE_IDXS.items()}

    def _get_adj_edges_from_edge_idx(self, edge_idx: EdgeIdx) -> Generator[Edge, None, None]:

        i_e_0, j_e_0 = _CatanBoard._EDGE_COORDS[edge_idx]

        for i_e, j_e in ((i_e_0, j_e_0 - 1), (i_e_0 + 1, j_e_0), (i_e_0 - 1, j_e_0 + 1), (i_e_0, j_e_0 + 1)):

            if 0 <= i_e < 11 and 0 <= j_e < 11:

                yield self._edge_matrix[i_e][j_e]

    def _get_adj_edges_from_vertex_idx(self, vertex_idx: VertexIdx) -> Generator[Edge, None, None]:

        i_v, j_v = _CatanBoard._VERTEX_COORDS[vertex_idx]
        i_e_0, j_e_0 = 2 * i_v, j_v

        for i_e, j_e in ((i_e_0, j_e_0 - 1), (i_e_0 - 1, j_e_0), (i_e_0, j_e_0)):

            if 0 <= i_e < 11 and 0 <= j_e < 11:

                yield self._edge_matrix[i_e][j_e]

    def _get_adj_vertices_from_edge_idx(self, edge_idx: EdgeIdx) -> tuple[Vertex, Vertex]:

        i_e_0, j_e_0 = _CatanBoard._EDGE_COORDS[edge_idx]

        # TODO

    def _get_adj_vertices_from_vertex_idx(self, vertex_idx: VertexIdx) -> Generator[Vertex, None, None]:

        i_v_0, j_v_0 = _CatanBoard._VERTEX_COORDS[vertex_idx]

        for i_v, j_v in ((i_v_0, j_v_0 - 1), (i_v_0 - 1, j_v_0), (i_v_0, j_v_0 + 1)):

            if 0 <= i_v < 6 and 0 <= j_v < 11:

                yield self._vertex_matrix[i_v][j_v]

    def _get_edge_matrix(self) -> list[list[Edge | None]]:

        return [
            [None, None, self._edges[0], self._edges[29], self._edges[28],
                self._edges[27], self._edges[26], self._edges[25], None, None, None],
            [None, None, self._edges[1], None, self._edges[41], None,
             self._edges[40], None, self._edges[24], None, None],
            [None, self._edges[2], self._edges[30], self._edges[42], self._edges[59],
             self._edges[58], self._edges[57], self._edges[39], self._edges[23], None, None],
            [None, self._edges[3], None, self._edges[43], None, self._edges[65],
             None, self._edges[56], None, self._edges[22], None],
            [self._edges[4], self._edges[31], self._edges[44], self._edges[60], self._edges[66],
             self._edges[71], self._edges[64], self._edges[55], self._edges[38], self._edges[21], None],
            [self._edges[5], None, self._edges[45], None, self._edges[67], None,
             self._edges[70], None, self._edges[54], None, self._edges[20], None],
            # TODO: 5 more rows
        ]

    def _get_tile_matrix(self) -> list[list[Tile | None]]:

        return [[self._tiles[0], self._tiles[11], self._tiles[10], None, None],
                [self._tiles[1], self._tiles[12],
                    self._tiles[17], self._tiles[9], None],
                [self._tiles[2], self._tiles[13], self._tiles[18],
                    self._tiles[16], self._tiles[8]],
                [None, self._tiles[3], self._tiles[14],
                    self._tiles[15], self._tiles[7]],
                [None, None, self._tiles[4], self._tiles[5], self._tiles[6]]]

    def _get_vertex_matrix(self) -> list[list[Vertex | None]]:

        return [
            [None, None, self._vertices[0], self._vertices[29], self._vertices[28], self._vertices[27],
                self._vertices[26], self._vertices[25], self._vertices[24], None, None],
            [None, self._vertices[2], self._vertices[1], self._vertices[30], self._vertices[47], self._vertices[46],
                self._vertices[45], self._vertices[44], self._vertices[23], self._vertices[22], None],
            [self._vertices[4], self._vertices[3], self._vertices[32], self._vertices[31], self._vertices[48], self._vertices[53],
                self._vertices[52], self._vertices[43], self._vertices[42], self._vertices[21], self._vertices[20]],
            [self._vertices[5], self._vertices[6], self._vertices[33], self._vertices[34], self._vertices[49], self._vertices[50],
                self._vertices[51], self._vertices[40], self._vertices[41], self._vertices[18], self._vertices[19]],
            [None, self._vertices[7], self._vertices[8], self._vertices[35], self._vertices[36], self._vertices[37],
                self._vertices[38], self._vertices[39], self._vertices[16], self._vertices[17], None],
            [None, None, self._vertices[9], self._vertices[10], self._vertices[11], self._vertices[12],
                self._vertices[13], self._vertices[14], self._vertices[15], None, None]
        ]

    def _get_vertices_from_tile_coords(self, tile_coords: tuple[int, int]) -> tuple[Vertex]:

        i_t, j_t = tile_coords
        i_v_0, j_v_0 = i_t, 2 * j_t + 2 - i_t

        return tuple(self._vertex_matrix[i_v][j_v] for i_v, j_v in ((i_v_0 + i // 3, j_v_0 + i % 3) for i in range(6)))


class Catan(_CatanBoard):
    """
    Represents the game Catan.
    """

    players: dict[Color, Player]
    turns: list[Color]

    def __init__(self, colors: list[Color]) -> None:
        """
        Creates an instance of a Catan game.

        :param colors: The colors of the players (in the order of their turns).
        """

        assert 2 <= len(
            colors) <= 4, f"Number of colors must be 2-4, got {len(colors)}."
        assert all(
            color in COLORS for color in colors), f"All colors must be one of {tuple(COLORS)}, got {colors}."

        super().__init__()

        self.players = {color: Player() for color in colors}
        self.turns = colors

        self._resources = [19] * 5
        self._largest_army_color = None
        self._longest_road_color = None

    def build_settlement(self, color: Color, vertex_idx: VertexIdx) -> None:
        """
        Builds a settlement.

        :param color: The color of the player.
        :param vertex_idx: The index of the vertex to build on.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."
        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        vertex = self._vertices[vertex_idx]
        player = self.players[color]

        resources = (LUMBER, BRICK, GRAIN, WOOL)
        costs = (-1,) * 4

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        assert all(player.resources[resource] > -cost for resource, cost in zip(resources, costs)
                   ), f"Player must have at least 1 lumber, 1 brick, 1 grain and 1 wool to build a settlement, has {player.resources[LUMBER]}l, {player.resources[BRICK]}b, {player.resources[GRAIN]}g and {player.resources[WOOL]}w."

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert any(edge.road == Road(color) for edge in self._get_adj_edges_from_vertex_idx(
            vertex_idx)), f"Vertex must have an adjacent road of the same color to build a settlement."

        assert all(vertex.building is None for vertex in self._get_adj_vertices_from_vertex_idx(
            vertex_idx)), f"Vertex must have no adjacent buildings to build a settlement."

        self.modify_resources(color, resources, costs)

        player.buildings_left[SETTLEMENT] -= 1

        vertex.building = Building(color, SETTLEMENT)

        player.victory_points += 1

        if vertex.harbor_type is not None:

            player.harbor_types.add(vertex.harbor_type)

    def build_road(self, color: Color, edge_idx: EdgeIdx) -> None:
        """
        Builds a road.

        :param color: The color of the player.
        :param edge_idx: The index of the edge to build on.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."
        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        edge = self._edges[edge_idx]
        player = self.players[color]

        assert player.roads_left > 0, f"Player does not have any roads left."

        costs = {LUMBER: -1, BRICK: -1}

        assert all(player.resources[resource_type] > -cost for resource_type,
                   cost in costs), f"Player must have at least 1 lumber and 1 brick to build a road, has {player.resources[LUMBER]}l and {player.resources[BRICK]}b."

        assert edge.road is None, f"Edge must be unoccupied to build a road."

        assert any(edge.road is not None and edge.road.color == color for edge in self._get_adj_edges_from_edge_idx(
            edge_idx)), f"Edge must have an adjacent road of the same color to build a road."

        self.modify_resources(color, costs)

        player.roads_left -= 1

        edge.road = Road(color)

        adj_vertices = self._get_adj_vertices_from_edge_idx(edge_idx)

        for i in range(2):

            adj_vertices[i].longest_road = max(
                adj_vertices[i].longest_road, adj_vertices[not i].longest_road + 1)

            player.longest_road = max(
                player.longest_road, adj_vertices[i].longest_road)

        if player.longest_road >= 5 and (self._longest_road_color is None or self._longest_road_color != color and player.longest_road > self.players[self._longest_road_color].longest_road):

            self.players[self._longest_road_color].victory_points -= 2

            self._longest_road_color = color

            player.victory_points += 2

    def end_turn(self) -> None:
        """
        Changes the turn to the next player.
        """

        self.turns = self.turns[1:] + self.turns[:1]

    def modify_resources(self, color: Color, amounts: dict[ResourceType, int]) -> None:
        """
        Modifies the resources of a player.

        :param color: The color of the player.
        :param amounts: The amounts of resources to modify.
        """

        for resource_type, amount in amounts:

            self.players[color].resources[resource_type] += amount

            self._resources[resource_type] -= amount

    def move_robber(self, robber_idx: TileIdx) -> None:
        """
        Moves the robber.

        :param robber_idx: The index of the tile to move the robber to.
        """

        assert 0 <= robber_idx <= 18, f"Robber index must be 0-18, got {robber_idx}."

        self._tiles[self._robber_idx].has_robber = False
        self._tiles[robber_idx].has_robber = True

        self._robber_idx = robber_idx

    def produce_resources(self, roll: Roll) -> None:
        """
        Gives resources to players based on the roll.

        :param roll: The roll to produce resources for.
        """

        for tile in self._token_to_tile[roll]:

            if tile.has_robber:

                continue

            resource_type = RESOURCE_TYPES[tile.tile_type - 1]

            amounts = defaultdict(int)

            for vertex in tile.vertices:

                if vertex.building is not None:

                    building = vertex.building

                    amounts[building.color] += 1 if building.building_type == SETTLEMENT else 2

            if self._resources[resource_type] < sum(amounts.values()):

                if self._resources[resource_type] > 0 and len(amounts) == 1:

                    color = tuple(amounts)[0]
                    self.modify_resources(
                        color, {resource_type: self._resources[resource_type]})

                else:

                    continue

            else:

                for color, amount in amounts.items():

                    self.modify_resources(color, {resource_type: amount})

    def build_set_up_phase(self, color: Color, vertex_idx: VertexIdx, edge_idx: EdgeIdx, round_two: bool = False) -> None:
        """
        Builds a settlement and road in the set-up phase.

        :param color: The color of the player.
        :param vertex_idx: The index of the vertex to build the settlement on.
        :param edge_idx: The index of the edge to build the road on.
        :param round_two: Whether or not this is the second round of the set-up phase.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."
        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        vertex = self._vertices[vertex_idx]
        player = self.players[color]

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert any(edge.road == Road(color) for edge in self._get_adj_edges_from_vertex_idx(
            vertex_idx)), f"Vertex must have an adjacent road of the same color to build a settlement."

        assert all(vertex.building is None for vertex in self._get_adj_vertices_from_vertex_idx(
            vertex_idx)), f"Vertex must have no adjacent buildings to build a settlement."

    def upgrade_settlement(self, color: Color, vertex_idx: VertexIdx) -> None:

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."
        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        vertex = self._vertices[vertex_idx]
        player = self.players[color]

        costs = {GRAIN: -2, ORE: -3}

        assert player.buildings_left[CITY] > 0, f"Player does not have any cities left."

        assert all(player.resources[resource_type] > -cost for resource_type,
                   cost in costs), f"Player must have at least 2 grain and 3 ore to upgrade settlement, has {player.resources[GRAIN]}g and {player.resources[ORE]}o."

        assert vertex.building is not None and vertex.building == Building(
            color, CITY), f"Vertex must have a settlement of the same color to upgrade settlement."

        self.modify_resources(color, costs)

        player.buildings_left[SETTLEMENT] += 1
        player.buildings_left[CITY] -= 1

        vertex.building.building_type = CITY

        player.victory_points += 1

    @property
    def is_game_over(self) -> bool:
        """
        Gets whether the game is over.

        :return: Whether or not the game is over.
        """

        return self.winner is not None

    @property
    def turn(self) -> Color:
        """
        Gets the current turn.

        :return: The color of the current turn.
        """

        return self.turns[0]

    @property
    def winner(self) -> Color | None:
        """
        Gets the winner of the game.

        :return: The winner of the game, or None if there isn't one.
        """

        for color, player in self.players.items():

            if player.victory_points >= 10:

                return color

        return None

    @staticmethod
    def roll_dice() -> Roll:
        """
        Rolls two six-sided dice.

        :return: The result of the dice roll.
        """

        return randint(1, 6) + randint(1, 6)


catan = Catan([BLUE, ORANGE])
