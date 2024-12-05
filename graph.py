from collections import defaultdict

class Graph:
    
    def __init__(self, polygons):
        self.polygons = defaultdict(set)
        self.graph = defaultdict(set)
        self.edges = set()
        self._build_graph(polygons)

    def _build_graph(self, polygons):
        polygon_id = 0
        for polygon in polygons:
            self._process_polygon(polygon, polygon_id)
            if len(polygon) > 2:
                polygon_id += 1

    def _process_polygon(self, polygon, polygon_id):
        if len(polygon) > 1 and polygon[0] == polygon[-1]:
            polygon.pop()
        num_points = len(polygon)
        for index, point in enumerate(polygon):
            sibling = polygon[(index + 1) % num_points]
            edge = Edge(point, sibling)
            self._add_polygon_data(point, sibling, edge, polygon_id, num_points)
            self.add_edge(edge)

    def _add_polygon_data(self, point, sibling, edge, polygon_id, num_points):
        if num_points > 2:
            point.polygon_id = polygon_id
            sibling.polygon_id = polygon_id
            self.polygons[polygon_id].add(edge)

    def get_adjacent_points(self, point):
        return [edge.get_adjacent(point) for edge in self.graph.get(point, [])]

    def get_points(self):
        return list(self.graph)

    def get_edges(self):
        return list(self.edges)

    def add_edge(self, edge):
        self.graph[edge.p1].add(edge)
        self.graph[edge.p2].add(edge)
        self.edges.add(edge)

    def __contains__(self, item):
        if isinstance(item, Point):
            return item in self.graph
        if isinstance(item, Edge):
            return item in self.edges
        return False

    def __getitem__(self, point):
        return self.graph.get(point, set())

    def __repr__(self):
        return "\n".join(f"{point}: {list(edges)}" for point, edges in self.graph.items())

    def __str__(self):
        return repr(self)


class Point:
    
    __slots__ = ('x', 'y', 'polygon_id')

    def __init__(self, x, y, polygon_id=-1):
        self.x = float(x)
        self.y = float(y)
        self.polygon_id = polygon_id

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"


class Edge:
    
    __slots__ = ('p1', 'p2')

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def get_adjacent(self, point):
        return self.p2 if point == self.p1 else self.p1

    def __contains__(self, point):
        return point in (self.p1, self.p2)

    def __eq__(self, other):
        return isinstance(other, Edge) and (
            {self.p1, self.p2} == {other.p1, other.p2}
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.p1, self.p2))

    def __repr__(self):
        return f"Edge({repr(self.p1)}, {repr(self.p2)})"

    def __str__(self):
        return f"({self.p1}, {self.p2})"