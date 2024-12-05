from graph import Point
from vis_graph import VisGraph
from haversine import haversine

# In this example we will find the shortest path between two points on a
# sphere, i.e. on earth. To calculate the total distance of that path, we
# need to use the great circle formula. We use the haversine package for this. 

# Example points
start_point = Point(-8.9316, 37.0088)
end_point = Point(103.851959, 1.290270)

# Load the visibility graph file. If you do not have this, please run 
# 1_build_graph_from_shapefiles.py first.
graph = VisGraph()
graph.load('GSHHS_c_L1.graph')

# Get the shortest path
shortest_path = graph.shortest_path(start_point, end_point)

# Calculate the total distance of the shortest path in km
path_distance = 0
prev_point = shortest_path[0]
for point in shortest_path[1:]:
    # Add miles=True to the end of the haversine call to get result in miles
    path_distance += haversine((prev_point.y, prev_point.x), (point.y, point.x))
    prev_point = point
# If you want to total distance in nautical miles:
# path_distance = path_distance*0.539957

print('Shortest path distance: {}'.format(path_distance))