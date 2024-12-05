import pygame
import sys
from graph import Point
from vis_graph import VisGraph
from visible_vertices import visible_vertices

pygame.init()

WIDTH, HEIGHT = 1440, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (230,230,250)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Polygon and Shortest Path Finder")

font = pygame.font.SysFont(None, 30)

button_height = 40
buttons = [
    {"label": "Select Start Point", "rect": pygame.Rect(10, 10, 200, button_height)},
    {"label": "Select End Point", "rect": pygame.Rect(220, 10, 200, button_height)},
    {"label": "Calculate Shortest Path", "rect": pygame.Rect(430, 10, 250, button_height)},
    {"label": "Draw Visibility Graph", "rect": pygame.Rect(690, 10, 250, button_height)},
    {"label": "Reset", "rect": pygame.Rect(950, 10, 100, button_height)},
]


selecting_start = False
selecting_end = False
start_point = None
end_point = None
points = []
polygons = []
current_nodes = []
shortest_path = []
visibility_graph_edges = []
visibility_light =[]


def draw_buttons():
    for button in buttons:
        color = BUTTON_HOVER if button["rect"].collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button["rect"])
        text = font.render(button["label"], True, BLACK)
        screen.blit(text, text.get_rect(center=button["rect"].center))

def draw_visibility_graph(path):
    for i in range(len(path) - 1):
        start = (path[i].x, HEIGHT - path[i].y)
        end = (path[i + 1].x, HEIGHT - path[i + 1].y)
        pygame.draw.line(screen, GREEN, start, end, 3)


def parse_visibility_graph(data):
    graph = {}
    for line in data.strip().split("\n"):
        # Split the line into parent and edges
        parent, edges = line.split(":")
        parent_node = tuple(map(float, parent.strip("()").replace(")", "").replace("(", "").split(", ")))

        # Parse the edges (child nodes)
        edges_list = [
            tuple(map(float, edge.strip("()").replace(")", "").replace("(", "").split(", ")))
            for edge in edges.strip().split(")(")
        ]

        graph[parent_node] = edges_list

    return graph



def draw_visibility_graph_visible(graph):
    # Iterate through each edge in the graph (list of tuples of Points)
    for edge in graph:  
        start_pos = (int(edge[0].x), HEIGHT - int(edge[0].y))  # Convert start point to screen coordinates
        end_pos = (int(edge[1].x), HEIGHT - int(edge[1].y))  # Convert end point to screen coordinates

        # Draw the line connecting the start and end of the edge
        pygame.draw.line(screen, YELLOW, start_pos, end_pos, 1)

def main():
    global selecting_start, selecting_end, start_point, end_point, points, current_nodes, polygons, shortest_path, visibility_graph_edges,visibility_light
    running = True
    vis_graph_built = False

    while running:
        screen.fill(WHITE)

        # Draw polygons
        for polygon in polygons:
            if len(polygon) > 2:
                pygame.draw.polygon(screen, BLACK, polygon, 2)
            for node in polygon:
                pygame.draw.circle(screen, RED, node, 5)

        # Draw current polygon being created
        if len(current_nodes) > 1:
            pygame.draw.lines(screen, BLUE, False, current_nodes, 4)
        for node in current_nodes:
            pygame.draw.circle(screen, RED, node, 5)

        # Draw start and end points
        if start_point:
            pygame.draw.circle(screen, GREEN, start_point, 10)
        if end_point:
            pygame.draw.circle(screen, BLUE, end_point, 10)

        # Draw visibility graph edges
        if visibility_graph_edges:
            for edge in visibility_graph_edges:
                start = (edge[0].x, HEIGHT - edge[0].y)
                end = (edge[1].x, HEIGHT - edge[1].y)
                pygame.draw.line(screen, BLACK, start, end, 1)

        # Draw visibility graph and shortest path
        if shortest_path:
            draw_visibility_graph(shortest_path)

        if visibility_light:
            draw_visibility_graph_visible(visibility_light)    



        draw_buttons()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button["rect"].collidepoint(event.pos):
                        if i == 0:
                            selecting_start = True
                            selecting_end = False
                        elif i == 1:
                            selecting_start = False
                            selecting_end = True
                        elif i == 2:
                            if start_point and end_point:
                                # Build visibility graph and calculate shortest path
                                polys = [
                                    [Point(node[0], HEIGHT - node[1]) for node in poly]
                                    for poly in polygons
                                ]
                                g = VisGraph()
                                g.build(polys)
                                shortest_path = g.shortest_path(
                                    Point(start_point[0], HEIGHT - start_point[1]),
                                    Point(end_point[0], HEIGHT - end_point[1]),
                                )
                                print("Shortest Path:", shortest_path)
                            else:
                                print("Start and End Points must be defined.")
                        elif i == 3:
                            # Build and display the visibility graph
                            polys = [
                                [Point(node[0], HEIGHT - node[1]) for node in poly]
                                for poly in polygons
                            ]
                            g = VisGraph()
                            g.build(polys)
                            
                            v1 = g.graph
                            v2 = g.pts
                            visibility_light = []
    
                            for p1 in v2:
                                 for p2 in visible_vertices(p1, v1):
                                    visibility_light.append((p1, p2))
                
                        elif i == 4:
                            start_point = None
                            end_point = None
                            points = []
                            polygons = []
                            current_nodes = []
                            shortest_path = []
                            visibility_graph_edges = []
                            visibility_light=[]

                if not any(button["rect"].collidepoint(event.pos) for button in buttons):
                    if selecting_start and event.button == 1:
                        start_point = event.pos
                        print(f"Start Point set to: {start_point}")
                        selecting_start = False
                    elif selecting_end and event.button == 1:
                        end_point = event.pos
                        print(f"End Point set to: {end_point}")
                        selecting_end = False
                    elif event.button == 3:
                        # Add point to current polygon
                        pos = pygame.mouse.get_pos()
                        if len(current_nodes) > 2 and current_nodes[0] == current_nodes[-1]:
                            current_nodes = []
                        current_nodes.append(pos)
                        points.append(pos)
                    elif event.button == 1:
                        # Complete the current polygon
                        if len(current_nodes) > 2:
                            current_nodes.append(current_nodes[0])
                            polygons.append(current_nodes)
                            current_nodes = []

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()