from timeit import default_timer
from multiprocessing import Pool
from tqdm import tqdm
from warnings import warn

from graph import Graph, Edge
from shortest_path import shortest_path
from visible_vertices import visible_vertices


class VisGraph:
    """
    Class representing a visibility graph for pathfinding and visibility checks.
    """

    def __init__(self):
        self.graph = None  # Graph representing the obstacles
        self.visgraph = None  # Visibility graph
        self.points = None  # Points from the obstacle graph
        self.pts = None

    def build(self, input_data, workers=1, show_progress=True):
        """
        Build the visibility graph from input obstacle data.

        :param input_data: List of polygons representing obstacles.
        :param workers: Number of parallel workers (1 for single-threaded).
        :param show_progress: Whether to display progress bar.
        """
        self.graph = Graph(input_data)
        self.visgraph = Graph([])
        self.points = self.graph.get_points()
        self.pts = self.points

        batch_size = 10
        point_batches = [self.points[i:i + batch_size] for i in range(0, len(self.points), batch_size)]

        if workers == 1:
            for batch in tqdm(point_batches, disable=not show_progress, desc="Building visibility graph"):
                for edge in _generate_visibility_edges(self.graph, batch):
                    self.visgraph.add_edge(edge)
        else:
            with Pool(workers) as pool:
                results = list(
                    tqdm(
                        pool.imap(_process_visibility_batch, [(self.graph, batch) for batch in point_batches]),
                        total=len(point_batches),
                        disable=not show_progress,
                        desc="Building visibility graph (parallel)",
                    )
                )
                for result in results:
                    for edge in result:
                        self.visgraph.add_edge(edge)

    def shortest_path(self, origin, destination):
        """
        Compute the shortest path between two points, considering visibility.

        :param origin: Starting point.
        :param destination: Destination point.
        :return: List of points representing the shortest path.
        """
        origin_exists = origin in self.visgraph
        dest_exists = destination in self.visgraph

        if origin_exists and dest_exists:
            return shortest_path(self.visgraph, origin, destination)

        additional_graph = Graph([])

        if not origin_exists:
            visible_from_origin = visible_vertices(origin, self.graph, destination=destination)
            for vertex in visible_from_origin:
                additional_graph.add_edge(Edge(origin, vertex))

        if not dest_exists:
            visible_from_dest = visible_vertices(destination, self.graph, origin=origin)
            for vertex in visible_from_dest:
                additional_graph.add_edge(Edge(destination, vertex))

        return shortest_path(self.visgraph, origin, destination, add_to_visgraph=additional_graph)

    def find_visible(self, point):
        """
        Find vertices visible from a given point.

        :param point: The point of interest.
        :return: List of visible vertices.
        """
        return visible_vertices(point, self.graph)

    def save(self, filename):
        """
        Save the obstacle graph and visibility graph to a file.
        """
        with open(filename, 'wb') as file:
            pickle.dump((self.graph, self.visgraph), file, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        """
        Load the obstacle graph and visibility graph from a file.
        """
        with open(filename, 'rb') as file:
            self.graph, self.visgraph = pickle.load(file)


# Helper functions
def _generate_visibility_edges(graph, points):
    """
    Generate visibility edges for a given batch of points.

    :param graph: The graph representing obstacles.
    :param points: List of points for which visibility edges are calculated.
    :return: List of visibility edges.
    """
    edges = []
    for p1 in points:
        for p2 in visible_vertices(p1, graph):
            edges.append(Edge(p1, p2))
    return edges


def _process_visibility_batch(args):
    """
    Wrapper for processing visibility graph batches in parallel.

    :param args: Tuple containing the graph and batch of points.
    :return: List of visibility edges.
    """
    try:
        return _generate_visibility_edges(*args)
    except KeyboardInterrupt:
        pass