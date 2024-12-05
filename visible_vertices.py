from __future__ import division
from math import pi, sqrt, atan, acos
from graph import Point

INFINTY = 10000
CCW = 1     #counter-clockwise
CW = -1     #clockwise
CLNR = 0    #collinear
"""To address inaccuracies caused by floating-point representation errors,
    some functions require rounding or truncating floating-point numbers to 
    a specific tolerance level."""
CT = 10     #collision tolerance
T = 10**CT
T2 = 10.0**CT

class OpenEdges(object):
    
    def __init__(self):
        self._open_edges = []

    def insert(self, p1, p2, edge):
        self._open_edges.insert(self._index(p1, p2, edge), edge)

    def _less_than(self, p1, p2, edge1, edge2):
        """Return True if edge1 is smaller than edge2, False otherwise."""
        if edge1 == edge2:
            return False
        if not edge_intersect(p1, p2, edge2):
            return True
        edge1_dist = point_edge_distance(p1, p2, edge1)
        edge2_dist = point_edge_distance(p1, p2, edge2)
        if edge1_dist > edge2_dist:
            return False
        if edge1_dist < edge2_dist:
            return True
        # If the distance is equal, we need to compare on the edge tan_inverses.
        if edge1_dist == edge2_dist:
            if edge1.p1 in edge2:
                same_point = edge1.p1
            else:
                same_point = edge1.p2
            tan_inverse_edge1 = tan_inverse2(p1, p2, edge1.get_adjacent(same_point))
            tan_inverse_edge2 = tan_inverse2(p1, p2, edge2.get_adjacent(same_point))
            if tan_inverse_edge1 < tan_inverse_edge2:
                return True
            return False

    def _index(self, p1, p2, edge):
        lo, hi = 0, len(self._open_edges)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._less_than(p1, p2, edge, self._open_edges[mid]):
                hi = mid  # Narrow search range to the lower half
            else:
                lo = mid + 1  # Narrow search range to the upper half
        return lo
    
    def smallest(self):
        return self._open_edges[0]

    def __getitem__(self, index):
        return self._open_edges[index]
    
    def __len__(self):
        return len(self._open_edges)

    def delete(self, p1, p2, edge):
        index = self._index(p1, p2, edge) - 1
        if self._open_edges[index] == edge:
            del self._open_edges[index]

def visible_vertices(point, graph, origin=None, destination=None):
    
    edges = graph.get_edges()
    points = graph.get_points()
    if origin: points.append(origin)
    if destination: points.append(destination)
    points.sort(key=lambda p: (tan_inverse(point, p), edge_distance(point, p)))   # here points is like A(research paper)
    
    open_edges = OpenEdges() # it will our data structure E (research parer)
    point_inf = Point(INFINTY, point.y)
    for edge in edges:
        if point in edge: continue
        if edge_intersect(point, point_inf, edge):
            if on_segment(point, edge.p1, point_inf): continue
            if on_segment(point, edge.p2, point_inf): continue
            open_edges.insert(point, point_inf, edge)

    visible = []
    prev = None
    pv = None     #previous visible

    for p in points:
        if p == point: 
            continue

        # Update open_edges - remove clock wise edges incident on p
        if open_edges:
            for edge in graph[p]:
                if ccw(point, p, edge.get_adjacent(p)) == CW:
                    open_edges.delete(point, p, edge)

        # Check if p is visible from point
        is_visible = False
        # ...Non-collinear points
        if prev is None or ccw(point, prev, p) != CLNR or not on_segment(point, prev, p):
            if len(open_edges) == 0:
                is_visible = True
            elif not edge_intersect(point, p, open_edges.smallest()):
                is_visible = True
        # ...For collinear points, if previous point was not visible, p is not
        elif not pv:
            is_visible = False
        # ...For collinear points, if previous point was visible, need to check
        # that the edge from prev to p does not intersect any open edge.
        else:
            is_visible = True
            for edge in open_edges:
                if prev not in edge and edge_intersect(prev, p, edge):
                    is_visible = False
                    break
            if is_visible and edge_in_polygon(prev, p, graph):
                    is_visible = False

        # Check if the visible edge is interior to its polygon
        if is_visible and p not in graph.get_adjacent_points(point):
            is_visible = not edge_in_polygon(point, p, graph)

        if is_visible: visible.append(p)

        # Update open_edges - Add counter clock wise edges incident on p
        for edge in graph[p]:
            if (point not in edge):
                if ccw(point, p, edge.get_adjacent(p)) == CCW:
                    open_edges.insert(point, p, edge)
        prev = p
        pv = is_visible
    return visible


def polygon_crossing(p1, poly_edges):
    """Returns True if the point p1 lies inside the polygon defined by the edges in poly_edges. 
    The method uses the crossing number algorithm and considers edges that are 
    collinear with p1"""
    
    p2 = Point(INFINTY, p1.y)
    ic = 0      #intersection counts if odd then lying else outside the polygon
    for edge in poly_edges:
        q1 = edge.p2.y
        q2 = edge.p2.x
        q3 = edge.p1.y
        q4 = edge.p1.x
        if p1.y < q3:
            if p1.y < q1: continue
        if p1.y > q3:
            if p1.y > q1: continue
        if p1.x > q4:
            if p1.x > q2: continue
        edge_p1_clnr = (ccw(p1, edge.p1, p2) == CLNR)
        edge_p2_clnr = (ccw(p1, edge.p2, p2) == CLNR)
        if edge_p1_clnr and edge_p2_clnr: continue
        if edge_p1_clnr or edge_p2_clnr:
            collinear_point = edge.p1 if edge_p1_clnr else edge.p2
            if edge.get_adjacent(collinear_point).y > p1.y:
                ic += 1
        elif edge_intersect(p1, p2, edge):
            ic += 1
    if ic % 2 == 0:
        return False
    return True


def edge_in_polygon(p1, p2, graph):
    """Return true if the edge from p1 to p2 is interior to any polygon
    in graph."""
    if p1.polygon_id != p2.polygon_id:
        return False
    if p1.polygon_id == -1 or p2.polygon_id == -1:
        return False
    mid_point = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return polygon_crossing(mid_point, graph.polygons[p1.polygon_id])




def intersect_point(p1, p2, edge):
    """Return intersect Point where the edge from p1, p2 intersects edge"""
    if p1 in edge: return p1
    if p2 in edge: return p2
    if edge.p1.x == edge.p2.x:  #case 1: edge is vertical
        if p1.x == p2.x:        #parallel lines
            return None
        pslope = (p1.y - p2.y) / (p1.x - p2.x)
        intersect_x = edge.p1.x #x-axis is of line
        intersect_y = pslope * (intersect_x - p1.x) + p1.y  # y = mx + c
        return Point(intersect_x, intersect_y)

    if p1.x == p2.x:    #if p1, and p2 are on same x coordinate
        eslope = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
        intersect_x = p1.x
        intersect_y = eslope * (intersect_x - edge.p1.x) + edge.p1.y
        return Point(intersect_x, intersect_y)

    pslope = (p1.y - p2.y) / (p1.x - p2.x)
    eslope = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
    if eslope == pslope:
        return None
    intersect_x = (eslope * edge.p1.x - pslope * p1.x + p1.y - edge.p1.y) / (eslope - pslope)
    intersect_y = eslope * (intersect_x - edge.p1.x) + edge.p1.y
    return Point(intersect_x, intersect_y)


def point_edge_distance(p1, p2, edge):
    """Return the Eucledian distance from p1 to intersect point with edge.
    Assumes the line going from p1 to p2 intersects edge before reaching p2."""
    ip = intersect_point(p1, p2, edge)
    if ip is not None:
        return edge_distance(p1, ip)
    return 0


def tan_inverse(center, point):
    """Return the tan_inverse (radian) of point from center of the radian circle."""
    dx = point.x - center.x
    dy = point.y - center.y

    if dx == 0:
        return pi / 2 if dy > 0 else pi * 3 / 2
    elif dy == 0:
        return 0 if dx > 0 else pi

    angle = atan(dy / dx)
    if dx < 0:
        return pi + angle
    elif dy < 0:
        return 2 * pi + angle
    return angle


def tan_inverse2(point_a, point_b, point_c):
    """Return tan_inverse B (radian) between point_b and point_c.  """
    
    a = (point_c.x - point_b.x)*(point_c.x - point_b.x) + (point_c.y - point_b.y)*(point_c.y - point_b.y)
    b = (point_c.x - point_a.x)*(point_c.x - point_a.x) + (point_c.y - point_a.y)**2
    c = (point_b.x - point_a.x)**2 + (point_b.y - point_a.y)**2
    denom = 0.000001 # tending to zero
    if 2*sqrt(a) * sqrt(c) != 0:
        denom = 2*sqrt(a) * sqrt(c)
    cos_value = (a + c - b) / denom
    return acos(int(cos_value*T)/T2)


def ccw(A, B, C):
    """Determine orientation: 1 if counterclockwise, -1 if clockwise, 0 if collinear."""
    area = ((B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x))
    area = int(area * T) / T2  # Apply scaling and truncate for efficiency
    return 1 if area > 0 else -1 if area < 0 else 0


def edge_intersect(p1, q1, edge):
    """Check if the segment from p1 to q1 intersects with a given edge."""
    p2, q2 = edge.p1, edge.p2  # Extract the endpoints of the edge

    o1 = ccw(p1, q1, p2)
    o2 = ccw(p1, q1, q2)
    o3 = ccw(p2, q2, p1)
    o4 = ccw(p2, q2, q1)

    # General case: segments intersect if orientations differ
    if o1 != o2 and o3 != o4:
        return True

    # Special cases: Check collinearity and overlap
    if o1 == CLNR and on_segment(p1, p2, q1):
        return True
    if o2 == CLNR and on_segment(p1, q2, q1):
        return True
    if o3 == CLNR and on_segment(p2, p1, q2):
        return True
    if o4 == CLNR and on_segment(p2, q1, q2):
        return True

    return False


def on_segment(p, q, r):
    """Check if point q lies on segment pr when p, q, r are collinear."""
    return (p.x <= q.x <= r.x or r.x <= q.x <= p.x) and \
           (p.y <= q.y <= r.y or r.y <= q.y <= p.y)


def unit_vector(origin, target):
    """Calculate the unit vector from `origin` to `target`."""
    distance = edge_distance(origin, target)
    dx = (target.x - origin.x) / distance
    dy = (target.y - origin.y) / distance
    return Point(dx, dy)


def edge_distance(p1, p2):
    """Return the Euclidean distance between two Points."""
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return sqrt(dx * dx + dy * dy)