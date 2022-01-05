from __future__ import annotations
from dataclasses import dataclass, field
from random import randint, shuffle

# Add base lists as constants at top of file (harbors, tiles, dev cards)
# Make dev card class with type and bought_this_turn attrs
# Implement dev card class functionality (Instances in game list, bought_this_turn in buy method and end of turn)

Color = int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(4)

BuildingType: bool
BUILDING_TYPES = (CITY, SETTLEMENT) = [True, False]

HarborType = int
HARBOR_TYPES = (BRICK_H, LUMBER_H, ORE_H, GRAIN_H,
                WOOL_H, GENERIC_H) = range(6)

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

    def upgrade(self) -> None:

        assert self.building_type == SETTLEMENT, f"Building must be a settlement to upgrade"

        self.building_type = CITY


@dataclass
class Road:

    color: Color


@dataclass
class Tile:

    tile_type: TileType
    has_robber: bool = False

    adj_vertices: tuple[Vertex, Vertex, Vertex, Vertex,
                        Vertex, Vertex] = field(default_factory=tuple)


@dataclass
class Vertex:

    building: Building | None = None
    harbor_type: HarborType | None = None
    longest_road: int = 0

    adj_edges: tuple[Edge] = field(default_factory=tuple)
    adj_tiles: tuple[Tile] = field(default_factory=tuple)
    adj_vertices: tuple[Vertex] = field(default_factory=tuple)


@dataclass
class Edge:

    road: Road | None = None

    adj_edges: tuple[Edge] = field(default_factory=tuple)
    adj_vertices: tuple[Vertex, Vertex] = field(default_factory=tuple)


@dataclass
class Player:

    color: Color
    resources: list[int] = field(default_factory=lambda: [0] * 5)
    development_cards: list[DevelopmentCard] = field(default_factory=list)
    buildings_left: list[int] = field(default_factory=lambda: [5, 4])
    roads_left: int = 15
    harbor_types: set[HarborType] = field(default_factory=set)
    knights_played: int = 0
    longest_road: int = 0
    victory_points: int = 0


class _CatanBoard:  # TODO: Everything lol gl

    _BASE_TOKEN_TO_TILE_IDXS: dict[Roll, tuple[TileIdx]] = {2: (1,), 3: (3, 16), 4: (9, 13), 5: (0, 14), 6: (
        2, 15), 8: (4, 10), 9: (6, 12), 10: (5, 11), 11: (8, 17), 12: (7,)}

    _EDGE_COORDS: list[tuple[int, int]] = []  # TODO

    _TILE_COORDS: list[tuple[int, int]] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (
        3, 4), (2, 4), (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]

    _VERTEX_COORDS: list[tuple[int, int]] = [(0, 2), (1, 2), (1, 1), (2, 1), (2, 0), (3, 0), (3, 1), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (4, 8), (4, 9), (3, 9), (3, 10), (2, 10), (2, 9), (1, 9), (1, 8), (
        0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (2, 3), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (3, 7), (3, 8), (2, 8), (2, 7), (1, 7), (1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (2, 6), (2, 5)]

    _VERTEX_IDX_TO_HARBOR_IDX: dict[VertexIdx, HarborIdx] = {
        0: 0, 2: 1, 3: 1, 6: 2, 7: 2, 9: 3, 10: 3, 12: 4, 13: 4, 16: 5, 17: 5, 19: 6, 20: 6, 22: 7, 23: 7, 26: 8, 27: 8, 29: 0}

    _edges: tuple[Edge]
    _tiles: tuple[Tile]
    _vertices: tuple[Vertex]

    def __init__(self) -> None:

        harbor_types = list(HARBOR_TYPES[:-1]) + [GENERIC_H] * 4
        shuffle(harbor_types)

        self._vertices = [Vertex(harbor_type=harbor_types[_CatanBoard._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                                 if vertex_idx in _CatanBoard._VERTEX_IDX_TO_HARBOR_IDX else None) for vertex_idx in VERTEX_IDXS]

        self._edges = [Edge() for _ in EDGE_IDXS]

        tile_types = [DESERT] + [HILLS] * 3 + [FOREST] * 4 + \
            [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4
        shuffle(tile_types)

        self._tiles = ...

        desert_idx = tile_types.index(DESERT)
        self._token_to_tile = {roll: tuple(self._tiles[tile_idx + 1 if tile_idx >= desert_idx else tile_idx]
                                           for tile_idx in tile_idxs) for roll, tile_idxs in _CatanBoard._BASE_TOKEN_TO_TILE_IDXS.items()}


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

        self.players = {color: Player(color) for color in colors}
        self.turns = colors

        self._resources = [19] * 5
        self._development_cards = [KNIGHT] * 14 + [ROAD_BUILDING] * \
            2 + [YEAR_OF_PLENTY] * 2 + [MONOPOLY] * 2 + [VICTORY_POINT] * 5
        shuffle(self._development_cards)
        self._largest_army_color = None
        self._longest_road_color = None

    def _build_road(self, color: Color, edge_idx: EdgeIdx) -> None:

        player = self.players[color]
        edge = self._edges[edge_idx]

        player.roads_left -= 1

        edge.road = Road(color)

        for i in range(2):

            edge.adj_vertices[i].longest_road = max(
                edge.adj_vertices[i].longest_road, edge.adj_vertices[not i].longest_road + 1)

            player.longest_road = max(
                player.longest_road, edge.adj_vertices[i].longest_road)

        if player.longest_road >= 5 and (self._longest_road_color is None or self._longest_road_color != color and player.longest_road > self.players[self._longest_road_color].longest_road):

            self.players[self._longest_road_color].victory_points -= 2

            self._longest_road_color = color

            player.victory_points += 2

    def _build_settlement(self, color: Color, vertex_idx: VertexIdx) -> None:

        player = self.players[color]
        vertex = self._vertices[vertex_idx]

        player.buildings_left[SETTLEMENT] -= 1

        vertex.building = Building(color, SETTLEMENT)

        player.victory_points += 1

        if vertex.harbor_type is not None:

            player.harbor_types.add(vertex.harbor_type)

    def _modify_resources(self, color: Color, amounts: dict[ResourceType, int]) -> None:

        for resource_type, amount in amounts:

            self.players[color].resources[resource_type] += amount

            self._resources[resource_type] -= amount

    def build_road(self, color: Color, edge_idx: EdgeIdx) -> None:
        """
        Builds a road.

        :param color: The color of the player.
        :param edge_idx: The index of the edge to build on.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."

        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        player = self.players[color]

        assert player.roads_left > 0, f"Player does not have any roads left."

        edge = self._edges[edge_idx]

        assert edge.road is None, f"Edge must be unoccupied to build a road."

        assert any(adj_edge.road == Road(color) for adj_edge in edge.adj_edges) or any(adj_vertex.building in (Building(color), Building(color, CITY))
                                                                                       for adj_vertex in edge.adj_vertices), f"Edge must have an adjacent road, settlement, or city of the same color to build a road."

        costs = {LUMBER: 1, BRICK: 1}

        assert all(player.resources[resource_type] > cost for resource_type,
                   cost in costs), f"Player must have at least 1 lumber and 1 brick to build a road, has {player.resources[LUMBER]}l and {player.resources[BRICK]}b."

        self._modify_resources(
            color, {resource_type: -cost for resource_type, cost in costs})

        self._build_road(color, edge_idx)

    def build_settlement(self, color: Color, vertex_idx: VertexIdx) -> None:
        """
        Builds a settlement.

        :param color: The color of the player.
        :param vertex_idx: The index of the vertex to build on.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."

        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        player = self.players[color]

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        vertex = self._vertices[vertex_idx]

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert any(adj_edge.road == Road(color)
                   for adj_edge in vertex.adj_edges), f"Vertex must have an adjacent road of the same color to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices), f"Vertex must have no adjacent buildings to build a settlement."

        costs = {LUMBER: 1, BRICK: 1, GRAIN: 1, WOOL: 1}

        assert all(player.resources[resource] > cost for resource,
                   cost in costs), f"Player must have at least 1 lumber, 1 brick, 1 grain and 1 wool to build a settlement, has {player.resources[LUMBER]}l, {player.resources[BRICK]}b, {player.resources[GRAIN]}g and {player.resources[WOOL]}w."

        self._modify_resources(
            color, {resource_type: -cost for resource_type, cost in costs})

        self._build_settlement(color, vertex_idx)

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

        player = self.players[color]

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        vertex = self._vertices[vertex_idx]

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices), f"Vertex must have no adjacent buildings to build a settlement."

        assert any(
            self._edges[edge_idx] is adj_edge for adj_edge in vertex.adj_edges), f"Road must be built adjacent to the settlement."

        assert player.roads_left > 0, f"Player does not have any roads left."

        edge = self._edges[edge_idx]

        assert edge.road is None, f"Edge must be unoccupied to build a road."

        self._build_settlement(color, vertex_idx)
        self._build_road(color, edge_idx)

        if round_two:

            for adj_tile in vertex.adj_tiles:

                if adj_tile.tile_type != DESERT:

                    self._modify_resources(
                        color, {RESOURCE_TYPES[adj_tile.tile_type - 1]: +1})

    def buy_development_card(self, color: Color) -> None:

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."

        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        assert self._development_cards, f"There are no development cards left."

        player = self.players[color]
        costs = {GRAIN: 1, WOOL: 1, ORE: 1}

        assert all(player.resources[resource] > cost for resource,
                   cost in costs), f"Player must have at least 1 grain, 1 wool, and 1 ore to buy a development card, has {player.resources[GRAIN]}g, {player.resources[WOOL]}w and {player.resources[ORE]}o."

        self._modify_resources(
            color, {resource_type: -cost for resource_type, cost in costs})

        player.development_cards.append(self._development_cards.pop())

    def domestic_trade(self, color_1: Color, amounts_1: dict[ResourceType, int], color_2: Color, amounts_2: dict[ResourceType, int]) -> None:
        """
        Trades resources between two players.

        :param color_1: The color of the first player.
        :param amounts_1: The amounts of resources the first player is trading.
        :param color_2: The color of the second player.
        :param amounts_2: The amounts of resources the second player is trading.
        """

        assert color_1 in self.players, f"Color must be one of {tuple(self.players)}, got {color_1}."
        assert color_2 in self.players, f"Color must be one of {tuple(self.players)}, got {color_2}."

        assert self.turn == color_1, f"Turn must be {color_1}, is {self.turn}."

        assert all(amount > 0 for amount in amounts_1.values(
        )), f"Player 1's amounts must all be positive, got {amounts_1}."
        assert all(amount > 0 for amount in amounts_2.values(
        )), f"Player 2's amounts must all be positive, got {amounts_2}."

        assert len(amounts_1) > 0, f"Player 1 must trade at least 1 resource."
        assert len(amounts_2) > 0, f"Player 2 must trade at least 1 resource."

        assert all(self.players[color_1].resources[resource_type] >= amount for resource_type, amount in amounts_1.items(
        )), f"Player 1 does not have enough resources to trade {amounts_1}."
        assert all(self.players[color_2].resources[resource_type] >= amount for resource_type, amount in amounts_2.items(
        )), f"Player 2 does not have enough resources to trade {amounts_2}."

        for resource_type, amount in amounts_1:

            amounts_2[resource_type] = amounts_2.get(resource_type, 0) - amount

        for resource_type, amount in amounts_2:

            amounts_1[resource_type] = amounts_1.get(resource_type, 0) - amount

        self._modify_resources(color_1, amounts_2)
        self._modify_resources(color_2, amounts_1)

    def end_turn(self) -> None:
        """
        Changes the turn to the next player.
        """

        self.turns = self.turns[1:] + self.turns[:1]

    def maritime_trade(self, color: Color, resource_type_out: ResourceType, amount: int, resource_type_in: ResourceType) -> None:
        """
        Trades resources for a maritime trade.

        :param color: The color of the player.
        :param resource_type_out: The type of resource the player is trading out.
        :param amount: The amount of resources the player is trading out.
        :param resource_type_in: The type of resource the player is trading in.
        """

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."

        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        assert amount in (
            2, 3, 4), f"Amount must be one of (2, 3, 4), got {amount}."

        player = self.players[color]

        assert player.resources[
            resource_type_out] >= amount, f"Player does not have enough resources to trade {amount}, has {player.resources[resource_type_out]}."

        if amount == 2:

            assert HARBOR_TYPES[
                resource_type_out] in player.harbors, f"Player does not have a harbor of type {HARBOR_TYPES[resource_type_out]}."

        elif amount == 3:

            assert GENERIC_H in player.harbors, f"Player does not have a generic harbor."

        self._modify_resources(
            color, {resource_type_out: -amount, resource_type_in: +1} if resource_type_out != resource_type_in else {resource_type_out: -amount + 1})

    def move_robber(self, robber_idx: TileIdx) -> None:
        """
        Moves the robber.

        :param robber_idx: The index of the tile to move the robber to.
        """

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

            amounts = {}

            for adj_vertex in tile.adj_vertices:

                if adj_vertex.building is not None:

                    building = adj_vertex.building

                    amounts[building.color] = amounts.get(
                        building.color, 0) + (1 if building.building_type == SETTLEMENT else 2)

            if self._resources[resource_type] < sum(amounts.values()):

                if self._resources[resource_type] > 0 and len(amounts) == 1:

                    color = tuple(amounts)[0]
                    self._modify_resources(
                        color, {resource_type: self._resources[resource_type]})

                else:

                    continue

            else:

                for color, amount in amounts.items():

                    self._modify_resources(color, {resource_type: amount})

    def upgrade_settlement(self, color: Color, vertex_idx: VertexIdx) -> None:

        assert color in self.players, f"Color must be one of {tuple(self.players)}, got {color}."
        assert self.turn == color, f"Turn must be {color}, is {self.turn}."

        player = self.players[color]

        assert player.buildings_left[CITY] > 0, f"Player does not have any cities left."

        vertex = self._vertices[vertex_idx]

        assert vertex.building == Building(
            color, CITY), f"Vertex must have a settlement of the same color to upgrade settlement."

        costs = {GRAIN: 2, ORE: 3}

        assert all(player.resources[resource_type] > cost for resource_type,
                   cost in costs), f"Player must have at least 2 grain and 3 ore to upgrade settlement, has {player.resources[GRAIN]}g and {player.resources[ORE]}o."

        self._modify_resources(
            color, {resource_type: -cost for resource_type, cost in costs})

        player.buildings_left[SETTLEMENT] += 1
        player.buildings_left[CITY] -= 1

        vertex.building.upgrade()

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


print({'a': 1, 'a': 2})
