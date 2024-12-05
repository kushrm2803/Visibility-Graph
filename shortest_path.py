from heapq import heapify, heappush, heappop
from visible_vertices import edge_distance

try:
    # Check Python version compatibility
    dict.iteritems
    def iteritems(d):  # For Python 2
        return d.iteritems()
except AttributeError:
    def iteritems(d):  # For Python 3
        return iter(d.items())


def dijkstra(graph, origin, destination, add_to_visgraph=None):
    """Find shortest paths from origin to all vertices in the graph using Dijkstra's algorithm."""
    distances = {}  # Shortest distances to each vertex
    predecessors = {}  # Tracks the path
    priority_queue = PriorityDict()  # Priority queue for vertices
    priority_queue[origin] = 0  # Origin starts with distance 0

    while priority_queue:
        current_vertex = priority_queue.pop_smallest()
        distances[current_vertex] = priority_queue.get(current_vertex, 0)

        if current_vertex == destination:  # Stop if destination reached
            break

        # Get adjacent edges
        edges = graph[current_vertex]
        if add_to_visgraph is not None and current_vertex in add_to_visgraph:
            edges = edges | add_to_visgraph[current_vertex]

        # Relax edges
        for edge in edges:
            neighbor = edge.get_adjacent(current_vertex)
            path_length = distances[current_vertex] + edge_distance(current_vertex, neighbor)
            if neighbor in distances:  # Already visited
                if path_length < distances[neighbor]:
                    raise ValueError("Graph contains a negative weight cycle")
            elif neighbor not in priority_queue or path_length < priority_queue[neighbor]:
                priority_queue[neighbor] = path_length
                predecessors[neighbor] = current_vertex

    return distances, predecessors


def shortest_path(graph, origin, destination, add_to_visgraph=None):
    """Compute the shortest path from origin to destination."""
    
    distances, predecessors = dijkstra(graph, origin, destination, add_to_visgraph)
    path = []
    while destination:
        path.append(destination)
        if destination == origin:
            break
        destination = predecessors[destination]
    path.reverse()
    return path


class PriorityDict(dict):
    """Dictionary used as a priority queue, with support for priority updates."""
    
    def __init__(self, *args, **kwargs):
        super(PriorityDict, self).__init__(*args, **kwargs)
        self._rebuild_heap()

    def _rebuild_heap(self):
        self._heap = [(v, k) for k, v in iteritems(self)]
        heapify(self._heap)

    def smallest(self):
        """Retrieve the item with the smallest priority."""
        
        while self._heap:
            value, key = self._heap[0]
            if key in self and self[key] == value:
                return key
            heappop(self._heap)
        raise KeyError("PriorityDict is empty")

    def pop_smallest(self):
        """Remove and return the item with the smallest priority."""
        while self._heap:
            value, key = heappop(self._heap)
            if key in self and self[key] == value:
                del self[key]
                return key
        raise KeyError("PriorityDict is empty")

    def __setitem__(self, key, value):
        super(PriorityDict, self).__setitem__(key, value)
        if len(self._heap) < 2 * len(self):
            heappush(self._heap, (value, key))
        else:
            self._rebuild_heap()

    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
            return value
        return self[key]

    def update(self, *args, **kwargs):
        super(PriorityDict, self).update(*args, **kwargs)
        self._rebuild_heap()

    def __iter__(self):
        """Iterate over the keys in order of priority."""
        def iterator():
            while self:
                smallest = self.pop_smallest()
                yield smallest
        return iterator()