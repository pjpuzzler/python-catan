from __future__ import annotations
from dataclasses import dataclass, field
from random import choices, randint, shuffle
from typing import Sequence

Color = int
COLORS = (BLUE, ORANGE, RED, WHITE) = range(4)

BuildingType = bool
BUILDING_TYPES = (CITY, SETTLEMENT) = [True, False]

HarborType = int
HARBOR_TYPES = (BRICK_H, LUMBER_H, ORE_H, GRAIN_H,
                WOOL_H, GENERIC_H) = range(6)
BASE_HARBOR_TYPES = list(HARBOR_TYPES[:-1]) + [GENERIC_H] * 4

TileType = int
TILE_TYPES = (DESERT, HILLS, FOREST, MOUNTAINS, FIELDS, PASTURE) = range(6)
BASE_TILE_TYPES = [DESERT] + [HILLS] * 3 + [FOREST] * \
    4 + [MOUNTAINS] * 3 + [FIELDS] * 4 + [PASTURE] * 4

ResourceType = int
RESOURCE_TYPES = (BRICK, LUMBER, ORE, GRAIN, WOOL) = range(5)

DevelopmentCardType = int
DEVELOPMENT_CARD_TYPES = (KNIGHT, ROAD_BUILDING,
                          YEAR_OF_PLENTY, MONOPOLY, VICTORY_POINT) = range(5)
BASE_DEVELOPMENT_CARD_TYPES = [KNIGHT] * 14 + [ROAD_BUILDING] * \
    2 + [YEAR_OF_PLENTY] * 2 + [MONOPOLY] * 2 + [VICTORY_POINT] * 5

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

Roll = int


@dataclass
class Building:

    color: Color
    building_type: BuildingType = SETTLEMENT


@dataclass
class DevelopmentCard:

    development_card_type: DevelopmentCardType

    playable: bool = field(default=False, repr=False)


@dataclass
class Edge:

    road: Road | None = None

    adj_edges: tuple[Edge] | None = field(default=None, repr=False)
    adj_vertices: tuple[Vertex] | None = field(default=None, repr=False)


@dataclass
class Player:

    color: Color

    resource_amounts: list[int] = field(
        default_factory=lambda: [0] * 5, repr=False)
    development_cards: list[DevelopmentCard] = field(
        default_factory=list, repr=False)
    buildings_left: list[int] = field(
        default_factory=lambda: [5, 4], repr=False)
    roads_left: int = field(default=15, repr=False)
    harbor_types: set[HarborType] = field(default_factory=set, repr=False)
    knights_played: int = field(default=0, repr=False)
    longest_road: int = field(default=0, repr=False)
    victory_points: int = field(default=0, repr=False)


@dataclass
class Road:

    color: Color


@dataclass()
class Tile:

    tile_type: TileType
    has_robber: bool = False

    adj_vertices: tuple[Vertex] | None = field(default=None, repr=False)


@dataclass
class Vertex:

    building: Building | None = None
    harbor_type: HarborType | None = None

    longest_road: int = field(default=0, repr=False)
    adj_edges: tuple[Edge] | None = field(default=None, repr=False)
    adj_tiles: tuple[Tile] | None = field(default=None, repr=False)
    adj_vertices: tuple[Vertex] | None = field(default=None, repr=False)


class _CatanBoard:

    _BASE_ROLL_TO_TILE_IDXS: dict[Roll, tuple[TileIdx]] = {2: (1,), 3: (3, 16), 4: (9, 13), 5: (0, 14), 6: (
        2, 15), 8: (4, 10), 9: (6, 12), 10: (5, 11), 11: (8, 17), 12: (7,)}

    _EDGE_COORDS: list[tuple[int]] = [(0, 2), (1, 2), (2, 1), (3, 1), (4, 0), (5, 0), (6, 0), (7, 1), (8, 1), (9, 2), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (9, 8), (8, 8), (7, 9), (6, 9), (5, 10), (4, 9), (3, 9), (2, 8), (1, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (2, 2), (4, 1), (6, 1), (
        8, 2), (9, 4), (9, 6), (8, 7), (6, 8), (4, 8), (2, 7), (1, 6), (1, 4), (2, 3), (3, 3), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3), (8, 4), (8, 5), (8, 6), (7, 7), (6, 7), (5, 8), (4, 7), (3, 7), (2, 6), (2, 5), (2, 4), (4, 3), (6, 3), (7, 5), (6, 6), (4, 6), (3, 5), (4, 4), (5, 4), (6, 4), (6, 5), (5, 6), (4, 5)]

    _TILE_COORDS: list[tuple[int]] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (
        3, 4), (2, 4), (1, 3), (0, 2), (0, 1), (1, 1), (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (2, 2)]

    _VERTEX_COORDS: list[tuple[int]] = [(0, 2), (1, 2), (1, 1), (2, 1), (2, 0), (3, 0), (3, 1), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (4, 8), (4, 9), (3, 9), (3, 10), (2, 10), (2, 9), (1, 9), (1, 8), (
        0, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (1, 3), (2, 3), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (3, 7), (3, 8), (2, 8), (2, 7), (1, 7), (1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (3, 5), (3, 6), (2, 6), (2, 5)]

    _VERTEX_IDX_TO_HARBOR_IDX: dict[VertexIdx, HarborIdx] = {
        0: 0, 2: 1, 3: 1, 6: 2, 7: 2, 9: 3, 10: 3, 12: 4, 13: 4, 16: 5, 17: 5, 19: 6, 20: 6, 22: 7, 23: 7, 26: 8, 27: 8, 29: 0}

    edges: tuple[Edge]
    robber_tile: Tile
    roll_to_tile: dict[Roll, tuple[Tile]]
    tiles: tuple[Tile]
    vertices: tuple[Vertex]

    def __init__(self) -> None:

        harbor_types = BASE_HARBOR_TYPES[:]
        shuffle(harbor_types)

        tile_types = BASE_TILE_TYPES[:]
        shuffle(tile_types)

        self.edges = [Edge() for _ in EDGE_IDXS]
        self.tiles = [Tile(tile_type, has_robber=tile_type == DESERT)
                      for tile_type in tile_types]
        self.vertices = [Vertex(harbor_type=harbor_types[_CatanBoard._VERTEX_IDX_TO_HARBOR_IDX[vertex_idx]]
                                if vertex_idx in _CatanBoard._VERTEX_IDX_TO_HARBOR_IDX else None) for vertex_idx in VERTEX_IDXS]

        robber_tile_idx = tile_types.index(DESERT)

        self.robber_tile = self.tiles[robber_tile_idx]

        self.roll_to_tile = {roll: tuple(self.tiles[tile_idx + 1 if tile_idx >= robber_tile_idx else tile_idx]
                                         for tile_idx in tile_idxs) for roll, tile_idxs in _CatanBoard._BASE_ROLL_TO_TILE_IDXS.items()}

        for edge_idx, edge in enumerate(self.edges):

            edge.adj_edges = self._get_adj_edges_from_edge_idx(edge_idx)
            edge.adj_vertices = self._get_adj_vertices_from_edge_idx(edge_idx)

        for tile_idx, tile in enumerate(self.tiles):

            tile.adj_vertices = self._get_adj_vertices_from_tile_idx(tile_idx)

        for vertex_idx, vertex in enumerate(self.vertices):

            vertex.adj_edges = self._get_adj_edges_from_vertex_idx(vertex_idx)
            vertex.adj_tiles = self._get_adj_tiles_from_vertex_idx(vertex_idx)
            vertex.adj_vertices = self._get_adj_vertices_from_vertex_idx(
                vertex_idx)

    def __repr__(self) -> str:

        pass  # TODO

    def _get_adj_edges_from_edge_idx(self, edge_idx: EdgeIdx) -> tuple[Edge]:

        edge_i, edge_j = _CatanBoard._EDGE_COORDS[edge_idx]

        if edge_i % 2 == 1:  # vertical edge

            return tuple(self.edges[adj_edge_i][adj_edge_j] for adj_edge_i, adj_edge_j in ((edge_i - 1, edge_j), (edge_i + 1, edge_j), (edge_i - 1, edge_j - 1), (edge_i + 1, edge_j - 1)) if 0 <= adj_edge_i < 11 and 0 <= adj_edge_j < 11)

        # TODO

    def _get_adj_edges_from_vertex_idx(self, vertex_idx: VertexIdx) -> tuple[Edge]:

        raise NotImplementedError  # TODO

    def _get_adj_tiles_from_vertex_idx(self, vertex_idx: VertexIdx) -> tuple[Tile]:

        raise NotImplementedError  # TODO

    def _get_adj_vertices_from_edge_idx(self, edge_idx: EdgeIdx) -> tuple[Vertex]:

        raise NotImplementedError  # TODO

    def _get_adj_vertices_from_tile_idx(self, tile_idx: TileIdx) -> tuple[Vertex]:

        raise NotImplementedError  # TODO

    def _get_adj_vertices_from_vertex_idx(self, vertex_idx: VertexIdx) -> tuple[Vertex]:

        raise NotImplementedError  # TODO


class Catan(_CatanBoard):
    """
    Represents the game Catan.
    """

    development_cards: list[DevelopmentCard]
    edges: tuple[Edge]
    largest_army_player: Player | None
    longest_road_player: Player | None
    players: tuple[Player]
    resource_amounts: list[int]
    robber_tile: Tile
    tiles: tuple[Tile]
    roll_to_tile: dict[Roll, tuple[Tile]]
    vertices: tuple[Vertex]

    def __init__(self, colors: Sequence[Color]) -> None:
        """
        Creates an instance of a Catan game.

        :param colors: The colors of the players (in the order of their turns).
        """

        assert 2 <= len(
            colors) <= 4, f"Number of colors must be 2-4, got {len(colors)}."
        assert all(
            color in COLORS for color in colors), f"All colors must be one of {tuple(COLORS)}, got {colors}."

        super().__init__()

        self.players = tuple(Player(color) for color in colors)
        self.resource_amounts = [19] * 5
        self.development_cards = [DevelopmentCard(
            development_card_type) for development_card_type in BASE_DEVELOPMENT_CARD_TYPES]
        shuffle(self.development_cards)
        self.largest_army_player = None
        self.longest_road_player = None

    def _build_road(self, edge: Edge) -> None:

        player = self.turn

        player.roads_left -= 1

        edge.road = Road(player.color)

        stack = [edge]

        while stack:

            edge = stack.pop()

            for i in range(2):

                edge.adj_vertices[i].longest_road = max(
                    edge.adj_vertices[i].longest_road, edge.adj_vertices[not i].longest_road + 1)

                player.longest_road = max(
                    player.longest_road, edge.adj_vertices[i].longest_road)

            for adj_edge in edge.adj_edges:

                if adj_edge.road is not None:

                    stack.append(adj_edge)

        if player.longest_road >= 5 and (self.longest_road_player is None or self.longest_road_player is not player and player.longest_road > self.longest_road_player.longest_road):

            if self.longest_road_player is not None:

                self.longest_road_player.victory_points -= 2

            self.longest_road_player = player

            player.victory_points += 2

    def _build_settlement(self, vertex: Vertex) -> None:

        player = self.turn

        player.buildings_left[SETTLEMENT] -= 1

        vertex.building = Building(player.color, SETTLEMENT)

        player.victory_points += 1

        if vertex.harbor_type is not None:

            player.harbor_types.add(vertex.harbor_type)

    def _modify_resources(self, resource_amounts: dict[ResourceType, int]) -> None:

        player = self.turn

        for resource_type, resource_amount in resource_amounts:

            player.resource_amounts[resource_type] += resource_amount

            self.resource_amounts[resource_type] -= resource_amount

    def build_road(self, edge_idx: EdgeIdx) -> None:
        """
        Builds a road.

        :param edge_idx: The index of the edge to build on.
        """

        player = self.turn

        assert player.roads_left > 0, f"Player does not have any roads left."

        edge = self.edges[edge_idx]

        assert edge.road is None, f"Edge must be unoccupied to build a road."

        assert any(adj_edge.road == Road(player.color) for adj_edge in edge.adj_edges) or any(adj_vertex.building is not None and adj_vertex.building.color ==
                                                                                              player.color for adj_vertex in edge.adj_vertices), f"Edge must have an adjacent road, settlement, or city of the same color to build a road."

        costs = {LUMBER: 1, BRICK: 1}

        assert all(player.resource_amounts[resource_type] > cost for resource_type,
                   cost in costs), f"Player must have at least 1 lumber and 1 brick to build a road, has {player.resource_amounts[LUMBER]}l and {player.resource_amounts[BRICK]}b."

        self._modify_resources(
            player, {resource_type: -cost for resource_type, cost in costs})

        self._build_road(edge)

    def build_settlement(self, vertex_idx: VertexIdx) -> None:
        """
        Builds a settlement.

        :param vertex_idx: The index of the vertex to build on.
        """

        player = self.turn

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        vertex = self.vertices[vertex_idx]

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert any(adj_edge.road == Road(player.color)
                   for adj_edge in vertex.adj_edges), f"Vertex must have an adjacent road of the same color to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices), f"Vertex must have no adjacent buildings to build a settlement."

        costs = {LUMBER: 1, BRICK: 1, GRAIN: 1, WOOL: 1}

        assert all(player.resource_amounts[resource] > cost for resource,
                   cost in costs), f"Player must have at least 1 lumber, 1 brick, 1 grain and 1 wool to build a settlement, has {player.resource_amounts[LUMBER]}l, {player.resource_amounts[BRICK]}b, {player.resource_amounts[GRAIN]}g and {player.resource_amounts[WOOL]}w."

        self._modify_resources(
            player, {resource_type: -cost for resource_type, cost in costs})

        self._build_settlement(vertex)

    def build_set_up_phase(self, vertex_idx: VertexIdx, edge_idx: EdgeIdx, round_two: bool = False) -> None:
        """
        Builds a settlement and road in the set-up phase.

        :param vertex_idx: The index of the vertex to build the settlement on.
        :param edge_idx: The index of the edge to build the road on.
        :param round_two: Whether or not this is the second round of the set-up phase.
        """

        player = self.turn

        assert player.buildings_left[SETTLEMENT] > 0, f"Player does not have any settlements left."

        vertex = self.vertices[vertex_idx]

        assert vertex.building is None, f"Vertex must be unoccupied to build a settlement."

        assert all(
            adj_vertex.building is None for adj_vertex in vertex.adj_vertices), f"Vertex must have no adjacent buildings to build a settlement."

        assert player.roads_left > 0, f"Player does not have any roads left."

        edge = self.edges[edge_idx]

        assert any(
            adj_edge is edge for adj_edge in vertex.adj_edges), f"Road must be built adjacent to the settlement."

        assert edge.road is None, f"Edge must be unoccupied to build a road."

        self._build_settlement(vertex)
        self._build_road(edge)

        if round_two:

            for adj_tile in vertex.adj_tiles:

                if adj_tile.tile_type != DESERT:

                    self._modify_resources(
                        player, {RESOURCE_TYPES[adj_tile.tile_type - 1]: +1})

    def buy_development_card(self) -> None:

        player = self.turn

        costs = {GRAIN: 1, WOOL: 1, ORE: 1}

        assert all(player.resource_amounts[resource] > cost for resource,
                   cost in costs), f"Player must have at least 1 grain, 1 wool, and 1 ore to buy a development card, has {player.resource_amounts[GRAIN]}g, {player.resource_amounts[WOOL]}w and {player.resource_amounts[ORE]}o."

        self._modify_resources(
            player, {resource_type: -cost for resource_type, cost in costs})

        development_card = self.development_cards.pop()
        player.development_cards.append(development_card)

        if development_card.development_card_type == VICTORY_POINT:

            player.victory_points += 1

    def domestic_trade(self, resource_amounts_out: dict[ResourceType, int], player_to_trade_with_idx: PlayerIdx, resource_amounts_in: dict[ResourceType, int]) -> None:
        """
        Trades resources between two players.

        :param resource_amounts_out: The amounts of resources the player is trading away.
        :param player_to_trade_with_idx: The index of the player to trade with.
        :param resource_amounts_in: The amounts of resources the player is receiving.
        """

        assert 1 <= player_to_trade_with_idx < len(
            self.players), f"Player to trade with index must be one of {tuple(range(1, len(self.players)))}, got {player_to_trade_with_idx}."

        assert all(amount > 0 for amount in resource_amounts_out.values(
        )), f"Player 1's resource amounts must all be positive, got {resource_amounts_out}."
        assert all(amount > 0 for amount in resource_amounts_in.values(
        )), f"Player 2's resource amounts must all be positive, got {resource_amounts_in}."

        assert len(
            resource_amounts_out) > 0, f"Player 1 must trade at least 1 resource."
        assert len(
            resource_amounts_in) > 0, f"Player 2 must trade at least 1 resource."

        player = self.turn
        player_to_trade_with = self.players[player_to_trade_with_idx]

        assert all(player.resource_amounts[resource_type] >= amount for resource_type, amount in resource_amounts_out.items(
        )), f"Player does not have enough resources to trade away, {resource_amounts_out}."
        assert all(player_to_trade_with.resource_amounts[resource_type] >= amount for resource_type, amount in resource_amounts_in.items(
        )), f"Player to trade with does not have enough resources to trade, {resource_amounts_in}."

        for resource_type, amount in resource_amounts_out:

            resource_amounts_in[resource_type] = resource_amounts_in.get(
                resource_type, 0) - amount

        for resource_type, amount in resource_amounts_in:

            resource_amounts_out[resource_type] = resource_amounts_out.get(
                resource_type, 0) - amount

        self._modify_resources(player, resource_amounts_in)
        self._modify_resources(player_to_trade_with, resource_amounts_out)

    def end_turn(self) -> None:
        """
        Changes the turn to the next player.
        """

        for development_card in self.turn.development_cards:

            if development_card.development_card_type != VICTORY_POINT:

                development_card.playable = True

        self.players = self.players[1:] + self.players[:1]

    def maritime_trade(self, resource_type_out: ResourceType, resource_amount: int, resource_type_in: ResourceType) -> None:
        """
        Trades resources for a maritime trade.

        :param resource_type_out: The type of resource the player is trading out.
        :param resource_amount: The amount of resources the player is trading out.
        :param resource_type_in: The type of resource the player is trading in.
        """

        assert resource_amount in (
            2, 3, 4), f"Amount must be one of (2, 3, 4), got {resource_amount}."

        player = self.turn

        assert player.resource_amounts[
            resource_type_out] >= resource_amount, f"Player does not have enough resources to trade {resource_amount}, has {player.resource_amounts[resource_type_out]}."

        if resource_amount == 2:

            assert HARBOR_TYPES[
                resource_type_out] in player.harbor_types, f"Player does not have a harbor of type {HARBOR_TYPES[resource_type_out]}."

        elif resource_amount == 3:

            assert GENERIC_H in player.harbor_types, f"Player does not have a generic harbor."

        self._modify_resources(player, {resource_type_out: -resource_amount, resource_type_in: +1}
                               if resource_type_out != resource_type_in else {resource_type_out: -resource_amount + 1})

    def move_robber(self, new_robber_tile: Tile, color_to_take_from: Color | None) -> None:
        """
        Moves the robber.

        :param new_robber_tile: The tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from.
        """

        assert new_robber_tile is not self.robber_tile, f"Robber must not be on the same tile."

        if color_to_take_from is not None:

            assert any(adj_vertex.building is not None and adj_vertex.building.color ==
                       color_to_take_from for adj_vertex in new_robber_tile.adj_vertices), f"Player {color_to_take_from} does not have any buildilngs on the robber tile."

            player_to_take_from = self.players[color_to_take_from]

            assert any(
                player_to_take_from.resource_amounts), f"Player to take cards from does not have any resources."

            resource_type_to_take = choices(
                RESOURCE_TYPES, player_to_take_from.resource_amounts)

            player_to_take_from.resource_amounts[resource_type_to_take] -= 1
            self.turn.resource_amounts[resource_type_to_take] += 1

        self.robber_tile.has_robber = False
        new_robber_tile.has_robber = True

        self.robber_tile = new_robber_tile

    def play_knight(self, new_robber_tile: Tile, color_to_take_from: Color | None) -> None:
        """
        Plays a knight development card.

        :param new_robber_tile: The tile to move the robber to.
        :param color_to_take_from: The color of the player to take cards from.
        """

        player = self.turn

        assert DevelopmentCard(
            KNIGHT, True) in player.development_cards, f"Player must have a knight bought on a previous turn to play a knight."

        self.move_robber(new_robber_tile, color_to_take_from)

        player.development_cards.remove(DevelopmentCard(KNIGHT, True))

        player.knights_played += 1

        if player.knights_played >= 3 and (self.largest_army_player is None or self.largest_army_player is not player and player.knights_played > self.largest_army_player.knights_played):

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

        assert DevelopmentCard(
            MONOPOLY, True) in player.development_cards, f"Player must have a monopoly bought on a previous turn to play a monopoly."

        player.development_cards.remove(DevelopmentCard(MONOPOLY, True))

        total_resource_amount = 0

        for other_player in self.players:

            if other_player is not player:

                other_player_resource_amount = other_player.resource_amounts[resource_type]

                total_resource_amount += other_player_resource_amount

                self._modify_resources(
                    other_player, {resource_type: -other_player_resource_amount})

        self._modify_resources(player, {resource_type: +total_resource_amount})

    def play_road_building(self, edge_idx_1: EdgeIdx, edge_idx_2: EdgeIdx | None) -> None:
        """
        Plays a road building development card.

        :param edge_idx_1: The index of the first edge.
        :param edge_idx_2: The index of the second edge, or None if the player only has one road left.
        """

        player = self.turn

        assert DevelopmentCard(
            ROAD_BUILDING, True) in player.development_cards, f"Player must have a road building bought on a previous turn to play a road building."

        edge_1 = self.edges[edge_idx_1]

        assert edge_1.road is None, f"Edge 1 must be unoccupied to build a road."

        assert any(adj_edge.road == Road(player.color) for adj_edge in edge_1.adj_edges) or any(adj_vertex.building is not None and adj_vertex.building.color ==
                                                                                                player.color for adj_vertex in edge_1.adj_vertices), f"Edge 1 must have an adjacent road, settlement, or city of the same color to build a road."

        if edge_idx_2 is not None:

            assert player.roads_left >= 2, f"Player does not have enough roads left."

            edge_2 = self.edges[edge_idx_2]

            assert edge_2.road is None, f"Edge 2 must be unoccupied to build a road."

            assert any(adj_edge.road == Road(player.color) for adj_edge in edge_2.adj_edges) or any(adj_vertex.building is not None and adj_vertex.building.color ==
                                                                                                    player.color for adj_vertex in edge_2.adj_vertices), f"Edge 2 must have an adjacent road, settlement, or city of the same color to build a road."

        else:

            assert player.roads_left > 0, f"Player does not have any roads left."

        player.development_cards.remove(DevelopmentCard(ROAD_BUILDING, True))

        self._build_road(edge_1)

        if edge_idx_2 is not None:

            self._build_road(edge_2)

    def play_year_of_plenty(self, resource_type_1: ResourceType, resource_type_2: ResourceType | None) -> None:
        """
        Plays a year of plenty development card.

        :param resource_type_1: The type of resource to take.
        :param resource_type_2: The type of resource to take, or None if the bank only has one card left.
        """

        player = self.turn

        assert DevelopmentCard(
            YEAR_OF_PLENTY, True) in player.development_cards, f"Player must have a year of plenty bought on a previous turn to play a year of plenty."

        assert self.resource_amounts[resource_type_1] > 0, f"There are not enough cards to take."

        resource_amounts = {resource_type_1: 1}

        if resource_type_2 is not None:

            assert self.resource_amounts[resource_type_2] > 0, f"There are not enough cards to take."

            resource_amounts[resource_type_2] = 2 if resource_type_2 == resource_type_1 else 1

        player.development_cards.remove(DevelopmentCard(YEAR_OF_PLENTY, True))

        self._modify_resources(player, resource_amounts)

    def produce_resources(self, roll: Roll) -> None:
        """
        Gives resources to players based on the roll.

        :param roll: The roll to produce resources for.
        """

        for tile in self.roll_to_tile[roll]:

            if tile.has_robber:

                continue

            resource_type = RESOURCE_TYPES[tile.tile_type - 1]

            resource_amounts = {}

            for adj_vertex in tile.adj_vertices:

                if adj_vertex.building is not None:

                    building = adj_vertex.building

                    resource_amounts[building.color] = resource_amounts.get(
                        building.color, 0) + (1 if building.building_type == SETTLEMENT else 2)

            if self.resource_amounts[resource_type] < sum(resource_amounts.values()):

                if self.resource_amounts[resource_type] > 0 and len(resource_amounts) == 1:

                    color = tuple(resource_amounts)[0]
                    self._modify_resources(
                        color, {resource_type: self.resource_amounts[resource_type]})

                else:

                    continue

            else:

                for color, amount in resource_amounts.items():

                    self._modify_resources(color, {resource_type: amount})

    def upgrade_settlement(self, vertex_idx: VertexIdx) -> None:

        player = self.turn

        assert player.buildings_left[CITY] > 0, f"Player does not have any cities left."

        vertex = self.vertices[vertex_idx]

        assert vertex.building == Building(
            player.color), f"Vertex must have a settlement of the same color to upgrade settlement."

        costs = {GRAIN: 2, ORE: 3}

        assert all(player.resource_amounts[resource_type] > cost for resource_type,
                   cost in costs), f"Player must have at least 2 grain and 3 ore to upgrade settlement, has {player.resource_amounts[GRAIN]}g and {player.resource_amounts[ORE]}o."

        self._modify_resources(
            player, {resource_type: -cost for resource_type, cost in costs})

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
