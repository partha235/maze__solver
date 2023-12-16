import random
import svgwrite
import heapq

class MazeNode:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.distance = float('inf')
        self.visited = False
        self.is_enemy = False

    def __lt__(self, other):
        return self.distance < other.distance

def generate_random_maze(rows, cols, num_enemies):
    maze = [[MazeNode(row, col) for col in range(cols)] for row in range(rows)]

    # Connect nodes randomly to create a maze
    for row in range(rows):
        for col in range(cols):
            if col < cols - 1 and random.choice([True, False]):
                maze[row][col].right = maze[row][col + 1]
                maze[row][col + 1].left = maze[row][col]
            if row < rows - 1 and random.choice([True, False]):
                maze[row][col].down = maze[row + 1][col]
                maze[row + 1][col].up = maze[row][col]

    return maze

def generate_start_on_border(rows, cols):
    return (random.randint(1, rows - 2), 0)

def generate_end_on_border(rows, cols, start):
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top" and start[0] != 0:
        return (0, random.randint(1, cols - 2))
    elif side == "bottom" and start[0] != rows - 1:
        return (rows - 1, random.randint(1, cols - 2))
    elif side == "left" and start[1] != 0:
        return (random.randint(1, rows - 2), 0)
    elif side == "right" and start[1] != cols - 1:
        return (random.randint(1, rows - 2), cols - 1)
    else:
        return generate_end_on_border(rows, cols, start)

def dijkstra(maze, start, end):
    start_node = maze[start[0]][start[1]]
    end_node = maze[end[0]][end[1]]

    # Priority queue to store nodes based on their distances
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node.visited:
            continue

        current_node.visited = True
        current_node.distance = current_distance

        # Check if we reached the end
        if current_node == end_node:
            break

        # Check neighbors
        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        for neighbor in filter(None, neighbors):
            if not neighbor.visited and not neighbor.is_enemy:
                new_distance = current_distance + 1  # Cost is always 1 for non-enemy nodes
                if new_distance < neighbor.distance:
                    neighbor.distance = new_distance
                    heapq.heappush(priority_queue, (new_distance, neighbor))

    # Check if there is a path from start to end
    if end_node.distance == float('inf'):
        raise ValueError("No path found")

    # Reconstruct the path from end to start
    path = []
    current_node = end_node
    while current_node != start_node:
        path.append((current_node.row, current_node.col))
        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        current_node = min(filter(None, neighbors), key=lambda x: x.distance)

    path.append((start_node.row, start_node.col))
    return list(reversed(path))

def place_enemies_along_path(maze, path, min_enemies):
    # Place at least min_enemies along the calculated path
    enemies_placed = 0
    for row, col in path:
        if not maze[row][col].is_enemy:
            maze[row][col].is_enemy = True
            enemies_placed += 1
            if enemies_placed >= min_enemies:
                break

def visualize_maze_svg(maze, path, start, end, file_name='maze.svg'):
    cell_size = 20
    padding = 2

    dwg = svgwrite.Drawing(file_name, profile='tiny')
    dwg.viewbox(0, 0, cell_size * len(maze[0]), cell_size * len(maze))

    for row_index, row in enumerate(maze):
        for col_index, node in enumerate(row):
            x = col_index * cell_size
            y = row_index * cell_size

            # Draw walls
            if node.left is None:
                dwg.add(dwg.line((x, y), (x, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.right is None:
                dwg.add(dwg.line((x + cell_size, y), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.up is None:
                dwg.add(dwg.line((x, y), (x + cell_size, y), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.down is None:
                dwg.add(dwg.line((x, y + cell_size), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))

            # Draw enemies
            if node.is_enemy:
                dwg.add(dwg.circle(center=(x + cell_size / 2, y + cell_size / 2), r=cell_size / 2 - padding, fill=svgwrite.rgb(255, 0, 0, '%')))

    # Draw the path lines with thicker stroke
    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]
        x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
        x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
        dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 255, '%'), stroke_width=4))
    
    # Draw start and end points with flag emojis
    start_x, start_y = start[1] * cell_size + cell_size / 2, start[0] * cell_size + cell_size / 2
    end_x, end_y = end[1] * cell_size + cell_size / 2, end[0] * cell_size + cell_size / 2
    
    dwg.add(dwg.text('🚩', insert=(start_x - cell_size / 4, start_y - cell_size / 4), font_size=cell_size / 2, fill=svgwrite.rgb(255, 0, 0, '%')))
    dwg.add(dwg.text('🏁', insert=(end_x - cell_size / 4, end_y - cell_size / 4), font_size=cell_size / 2, fill=svgwrite.rgb(0, 255, 0, '%')))
    
    dwg.save()

# Example usage
rows, cols = 50, 50
num_enemies = 10
min_enemies_on_path = 2
random_maze = generate_random_maze(rows, cols, num_enemies)
start_point = generate_start_on_border(rows, cols)
end_point = generate_end_on_border(rows, cols, start_point)

try:
    shortest_path = dijkstra(random_maze, start_point, end_point)
    print("Start Point:", start_point)
    print("End Point:", end_point)
    print("Shortest Path without crossing any enemies:", shortest_path)
    
    # Place enemies along the calculated path
    place_enemies_along_path(random_maze, shortest_path, min_enemies_on_path)
    
    # Rerun Dijkstra's algorithm after placing enemies
    new_shortest_path = dijkstra(random_maze, start_point, end_point)
    print("Shortest Path with at least 2 enemies:", new_shortest_path)
    
    visualize_maze_svg(random_maze, new_shortest_path, start_point, end_point, file_name='maze.svg')
except ValueError as e:
    print(e)