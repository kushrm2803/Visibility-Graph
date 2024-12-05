from vis_graph import VisGraph
from graph import Point
import shapefile

def main():
    input_shapefile = shapefile.Reader('GSHHS_c_L1')
    output_graphfile = 'GSHHS_c_L1.graph'

    # Get the shoreline shapes from the shape file
    shapes = input_shapefile.shapes()
    print(f'The shapefile contains {len(shapes)} shapes.')

    # Create a list of polygons
    polygons = []
    for shape in shapes:
        polygon = []
        for point in shape.points:
            polygon.append(Point(point[0], point[1]))
        polygons.append(polygon)

    # Start building the visibility graph
    graph = VisGraph()
    print('Starting building visibility graph')
    graph.build(polygons, workers=12)  # Number of workers for parallel processing
    print('Finished building visibility graph')

    # Save the visibility graph to a file
    graph.save(output_graphfile)
    print(f'Saved visibility graph to file: {output_graphfile}')

if __name__ == '__main__':
    main()
