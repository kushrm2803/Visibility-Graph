from graph import Point
from vis_graph import VisGraph
import folium

# Example points
# Point(East, North)
start_point = Point(-8.9316, 37.0088)
# Point(West, North)
end_point = Point(103.851959, 1.290270)

# Load the visibility graph file. If you do not have this, please run
# 1_build_graph_from_shapefiles.py first.
graph = VisGraph()
graph.load('GSHHS_c_L1.graph')

# Calculate the shortest path
shortest_path = graph.shortest_path(start_point, end_point)

# Plot of the path using folium
geopath = [[point.y, point.x] for point in shortest_path]
geomap = folium.Map([0, 0], zoom_start=2)

# Add markers for the path
for point in geopath:
    folium.Marker(point, popup=str(point)).add_to(geomap)

# Add the polyline for the shortest path
folium.PolyLine(geopath, color="blue", weight=2.5, opacity=1).add_to(geomap)

# Add labeled markers for the start and end points
folium.Marker(
    geopath[0], 
    popup=f"Startpoint ({start_point.x}, {start_point.y})", 
    icon=folium.Icon(color='green')
).add_to(geomap)

folium.Marker(
    geopath[-1], 
    popup=f"EndPoint ({end_point.x}, {end_point.y})", 
    icon=folium.Icon(color='red')
).add_to(geomap)

# Save the interactive plot as a map
output_name = 'example_shortest_path_plot.html'
geomap.save(output_name)
print('Output saved to:', output_name)
