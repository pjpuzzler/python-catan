import catan
import math

_COORDS_TO_TILE_IDX = {
    (0, 0): 0,
    (0, 1): 1,
    (0, 2): 2,
    (1, 0): 11,
    (1, 1): 12,
    (1, 2): 13,
    (1, 3): 3,
    (2, 0): 10,
    (2, 1): 17,
    (2, 2): 18,
    (2, 3): 14,
    (2, 4): 4,
    (3, 0): 9,
    (3, 1): 16,
    (3, 2): 15,
    (3, 3): 5,
    (4, 0): 8,
    (4, 1): 7,
    (4, 2): 6,
}
_TILE_TYPE_COLORS = {
    catan.TileType.DESERT: "#dbca7b",
    catan.TileType.HILLS: "#d97c1e",
    catan.TileType.FOREST: "#197816",
    catan.TileType.MOUNTAINS: "#969696",
    catan.TileType.FIELDS: "#ebda28",
    catan.TileType.PASTURE: "#67eb50",
}
_HARBOR_TYPE_COLORS = {
    catan.HarborType.BRICK: "#c76136",
    catan.HarborType.LUMBER: "#634634",
    catan.HarborType.ORE: "#545454",
    catan.HarborType.GRAIN: "#ebda28",
    catan.HarborType.WOOL: "#bababa",
    catan.HarborType.GENERIC: "#106cc2",
}
_COLOR_COLORS = {
    catan.Color.BLUE: "#1a6edb",
    catan.Color.ORANGE: "#db7e1a",
    catan.Color.RED: "#de1d1d",
    catan.Color.WHITE: "#ffffff",
}


def _draw_hex(
    c,
    x,
    y,
    size,
    fill,
    number,
    rot,
    show_indices,
    row=None,
    col=None,
    visited_vertices=None,
    visited_edges=None,
    others=None,
    buildings=None,
    roads=None,
    indices=None,
):
    if row is not None and col is not None:
        tile_idx = _COORDS_TO_TILE_IDX[row, col]
    else:
        tile_idx = None
    if fill is None:
        tile = c.tiles[tile_idx]
        fill = _TILE_TYPE_COLORS[tile.tile_type]
        if tile.has_robber:
            others.append(
                f'<circle cx="{x}" cy="{y}" r="{size / 3}" fill="black" fill-opacity="0.4" />'
            )
    else:
        tile = None
    if number is None:
        number = c._tokens[tile_idx]
        if number is None:
            number = ""
    points = []
    for i in range(6):
        angle_deg = 60 * i + rot
        angle_rad = angle_deg * math.pi / 180
        point_x, point_y = x + size * math.cos(angle_rad), y + size * math.sin(
            angle_rad
        )
        points.append(point_x)
        points.append(point_y)
        if tile is not None:
            adj_vertex_idx = (i + 2) % 6
            vertex = tile.adj_vertices[adj_vertex_idx]
            (edge,) = set(vertex.adj_edges) & set(
                tile.adj_vertices[(adj_vertex_idx - 1) % 6].adj_edges
            )
            if vertex not in visited_vertices:
                if vertex.building is not None:
                    vx, vy = point_x - 7, point_y - 7 - 1
                    if vertex.building.building_type is catan.BuildingType.CITY:
                        # others.append(
                        #     f'<rect width="{s}" height="{s}" transform="rotate(45 {vx + s/2} {vy + s/2})" x="{vx}" y="{vy}" fill="{_COLOR_COLORS[vertex.building.color]}" />'
                        # )
                        ps = " ".join(
                            map(
                                str,
                                [
                                    vx - 7,
                                    vy,
                                    vx + 7,
                                    vy,
                                    vx + 7,
                                    vy - 6,
                                    vx + 14,
                                    vy - 7 - 6,
                                    vx + 21,
                                    vy - 6,
                                    vx + 21,
                                    vy + 14,
                                    vx - 7,
                                    vy + 14,
                                ],
                            )
                        )
                        buildings.append(
                            f'<polygon points="{ps}" fill="{_COLOR_COLORS[vertex.building.color]}" style="stroke:black" />'
                        )
                    else:
                        ps = " ".join(
                            map(
                                str,
                                [
                                    vx,
                                    vy,
                                    vx + 7,
                                    vy - 7,
                                    vx + 14,
                                    vy,
                                    vx + 14,
                                    vy + 14,
                                    vx,
                                    vy + 14,
                                ],
                            )
                        )
                        buildings.append(
                            f'<polygon points="{ps}" fill="{_COLOR_COLORS[vertex.building.color]}" style="stroke:black" />'
                        )
                if show_indices:
                    indices.append(
                        f'<text x="{point_x}" y="{point_y - 1}" font-size="{10}" fill="black" text-anchor="middle">{vertex.idx}</text>'
                    )
                visited_vertices.add(vertex)
            if i > 0 and edge not in visited_edges:
                x1, y1 = point_x, point_y
                x2, y2 = points[-4], points[-3]
                x_1_5, y_1_5 = x1 + (x2 - x1) * (1 / 5), y1 + (y2 - y1) * (1 / 5)
                x_4_5, y_4_5 = x1 + (x2 - x1) * (4 / 5), y1 + (y2 - y1) * (4 / 5)
                if edge.road is not None:
                    # roads.append(
                    #     f'<line x1="{x_1_5}" y1="{y_1_5}" x2="{x_4_5}" y2="{y_4_5}" stroke="black" stroke-width="10" stroke-linecap="square" />'
                    # )
                    roads.append(
                        f'<line x1="{x_1_5}" y1="{y_1_5}" x2="{x_4_5}" y2="{y_4_5}" stroke="{_COLOR_COLORS[edge.road.color]}" stroke-width="6" />'
                    )  # TODO: border
                if show_indices:
                    indices.append(
                        f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2}" font-size="{10}" fill="black" text-anchor="middle">{edge.idx}</text>'
                    )
                visited_edges.add(edge)

    if tile is not None:
        i = 0
        adj_vertex_idx = (i + 2) % 6
        vertex = tile.adj_vertices[adj_vertex_idx]
        (edge,) = set(vertex.adj_edges) & set(
            tile.adj_vertices[(adj_vertex_idx - 1) % 6].adj_edges
        )
        if edge not in visited_edges:
            x1, y1 = points[0], points[1]
            x2, y2 = points[-2], points[-1]
            x_1_5, y_1_5 = x1 + (x2 - x1) * (1 / 5), y1 + (y2 - y1) * (1 / 5)
            x_4_5, y_4_5 = x1 + (x2 - x1) * (4 / 5), y1 + (y2 - y1) * (4 / 5)
            if edge.road is not None:
                # roads.append(
                #     f'<line x1="{x_1_5}" y1="{y_1_5}" x2="{x_4_5}" y2="{y_4_5}" stroke="black" stroke-width="10" stroke-linecap="square" />'
                # )
                roads.append(
                    f'<line x1="{x_1_5}" y1="{y_1_5}" x2="{x_4_5}" y2="{y_4_5}" stroke="{_COLOR_COLORS[edge.road.color]}" stroke-width="6" />'
                )  # TODO: border
            if show_indices:
                indices.append(
                    f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2}" font-size="{10}" fill="black" text-anchor="middle">{edge.idx}</text>'
                )
            visited_edges.add(edge)
    points = " ".join(map(str, points))
    if number:
        number_fill = "red" if number in (6, 8) else "black"
        font_reduction = abs(int(number) - 7) * 3
    else:
        number_fill = "white"
        font_reduction = 0
    s = f'<polygon points="{points}" fill="{fill}" stroke="black" stroke-width="1" /><text x="{x}" y="{y+10-font_reduction/6}" font-size="{30-font_reduction}" fill="{number_fill}" text-anchor="middle">{number}</text>'
    if show_indices:
        s += f'<text x="{x}" y="{y+30-20/6}" font-size="{10}" fill="black" text-anchor="middle" font-weight="bold">{tile_idx}</text>'
    return s


def board(c: catan._CatanBoard, show_indices: bool) -> str:
    size = 50
    width = size * 0.8660254 * 2 * 5 + size * 2.5
    height = width * 0.8660254

    svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    svg += '<rect width="100%" height="100%" fill="#1f1f1f" />'

    svg += _draw_hex(c, width / 2, height / 2, width / 2, "#3c9cf0", "", 0, False)

    others, buildings, roads, indices = [], [], [], []

    harbor_colors = [
        _HARBOR_TYPE_COLORS[harbor_type] for harbor_type in c._harbor_types
    ]
    others.append(
        f'<line x1="156" y1="28" x2="192.40381056766577" y2="40.837062353868404" stroke-width="2" stroke="{harbor_colors[0]}"/>'
    )
    others.append(
        f'<line x1="156" y1="28" x2="149.10254037844385" y2="65.83706235386839" stroke-width="2" stroke="{harbor_colors[0]}"/>'
    )
    others.append(
        f'<circle cx="156" cy="28" r="{size / 3}" fill="{harbor_colors[0]}" ></circle><text x="156" y="33" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[0] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="315" y1="28" x2="279.00635094610965" y2="40.837062353868404" stroke-width="2" stroke="{harbor_colors[1]}"/>'
    )
    others.append(
        f'<line x1="315" y1="28" x2="322.30762113533154" y2="65.83706235386839" stroke-width="2" stroke="{harbor_colors[1]}"/>'
    )
    others.append(
        f'<circle cx="315" cy="28" r="{size / 3}" fill="{harbor_colors[1]}" ></circle><text x="315" y="33" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[1] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="445" y1="103" x2="408.9101615137755" y2="115.8370623538684" stroke-width="2" stroke="{harbor_colors[2]}"/>'
    )
    others.append(
        f'<line x1="445" y1="103" x2="452.21143170299734" y2="140.8370623538684" stroke-width="2" stroke="{harbor_colors[2]}"/>'
    )
    others.append(
        f'<circle cx="445" cy="103" r="{size / 3}" fill="{harbor_colors[2]}" ></circle><text x="445" y="108" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[2] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="524" y1="241" x2="495.51270189221924" y2="215.8370623538684" stroke-width="2" stroke="{harbor_colors[3]}"/>'
    )
    others.append(
        f'<line x1="524" y1="241" x2="495.5127018922193" y2="265.8370623538684" stroke-width="2" stroke="{harbor_colors[3]}"/>'
    )
    others.append(
        f'<circle cx="524" cy="241" r="{size / 3}" fill="{harbor_colors[3]}" ></circle><text x="524" y="246" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[3] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="445" y1="379" x2="452.2114317029974" y2="340.8370623538684" stroke-width="2" stroke="{harbor_colors[4]}"/>'
    )
    others.append(
        f'<line x1="445" y1="379" x2="408.91016151377545" y2="365.8370623538684" stroke-width="2" stroke="{harbor_colors[4]}"/>'
    )
    others.append(
        f'<circle cx="445" cy="379" r="{size / 3}" fill="{harbor_colors[4]}" ></circle><text x="445" y="384" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[4] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="315" y1="454" x2="322.3076211353316" y2="415.8370623538684" stroke-width="2" stroke="{harbor_colors[5]}"/>'
    )
    others.append(
        f'<line x1="315" y1="454" x2="279.00635094610965" y2="440.8370623538684" stroke-width="2" stroke="{harbor_colors[5]}"/>'
    )
    others.append(
        f'<circle cx="315" cy="454" r="{size / 3}" fill="{harbor_colors[5]}" ></circle><text x="315" y="459" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[5] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="156" y1="454" x2="192.40381056766577" y2="440.8370623538684" stroke-width="2" stroke="{harbor_colors[6]}"/>'
    )
    others.append(
        f'<line x1="156" y1="454" x2="149.10254037844385" y2="415.8370623538684" stroke-width="2" stroke="{harbor_colors[6]}"/>'
    )
    others.append(
        f'<circle cx="156" cy="454" r="{size / 3}" fill="{harbor_colors[6]}" ></circle><text x="156" y="459" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[6] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="78" y1="316" x2="105.80127018922191" y2="340.8370623538684" stroke-width="2" stroke="{harbor_colors[7]}"/>'
    )
    others.append(
        f'<line x1="78" y1="316" x2="105.80127018922192" y2="290.8370623538684" stroke-width="2" stroke="{harbor_colors[7]}"/>'
    )
    others.append(
        f'<circle cx="78" cy="316" r="{size / 3}" fill="{harbor_colors[7]}" ></circle><text x="78" y="321" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[7] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    others.append(
        f'<line x1="78" y1="166" x2="105.80127018922191" y2="190.83706235386842" stroke-width="2" stroke="{harbor_colors[8]}"/>'
    )
    others.append(
        f'<line x1="78" y1="166" x2="105.80127018922192" y2="140.83706235386842" stroke-width="2" stroke="{harbor_colors[8]}"/>'
    )
    others.append(
        f'<circle cx="78" cy="166" r="{size / 3}" fill="{harbor_colors[8]}" ></circle><text x="78" y="171" font-size="14" fill="black" text-anchor="middle">{3 if c._harbor_types[8] is catan.HarborType.GENERIC else 2}:1</text>'
    )

    x_offset = size * math.sqrt(3) + size * 1.25
    y_offset = height / 5.32
    visited_vertices = set()
    visited_edges = set()
    for row in range(5):
        if row == 0 or row == 4:
            cols = 3
        elif row == 1 or row == 3:
            cols = 4
        else:
            cols = 5
        for col in range(cols):
            x = x_offset + col * size * math.sqrt(3)
            y = y_offset + row * size * 1.5
            if row == 2:
                x -= size * math.sqrt(3) / 2
            elif row % 2 == 0:
                x += size * math.sqrt(3) / 2
            svg += _draw_hex(
                c,
                x,
                y,
                size,
                None,
                None,
                30,
                show_indices,
                row,
                col,
                visited_vertices,
                visited_edges,
                others,
                buildings,
                roads,
                indices,
            )

    svg += "".join(others)
    svg += "".join(roads)
    svg += "".join(buildings)
    svg += "".join(indices)
    svg += "</svg>"
    return svg
