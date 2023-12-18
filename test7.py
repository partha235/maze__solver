import random
import svgwrite
import heapq
import math


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
        self.is_reward = False

    def __lt__(self, other):
        return self.distance < other.distance

def generate_random_maze(rows, cols, num_enemies=10, num_rewards=5):
    maze = [[MazeNode(row, col) for col in range(cols)] for row in range(rows)]

    for row in range(rows):
        for col in range(cols):
            if col < cols - 1 and random.choice([True, False]):
                maze[row][col].right = maze[row][col + 1]
                maze[row][col + 1].left = maze[row][col]
            if row < rows - 1 and random.choice([True, False]):
                maze[row][col].down = maze[row + 1][col]
                maze[row + 1][col].up = maze[row][col]

    for _ in range(num_enemies):
        enemy_row = random.randint(0, rows - 1)
        enemy_col = random.randint(0, cols - 1)
        maze[enemy_row][enemy_col].is_enemy = True

    for _ in range(num_rewards):
        reward_row = random.randint(0, rows - 1)
        reward_col = random.randint(0, cols - 1)
        maze[reward_row][reward_col].is_reward = True

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

def heuristic(node, end):
    return math.sqrt(abs((node.row - end[0]) * 2 + (node.col - end[1]) * 2))

def astar(maze, start, end):
    for row in maze:
        for node in row:
            node.visited = False
            node.distance = float('inf')

    start_node = maze[start[0]][start[1]]
    end_node = maze[end[0]][end[1]]

    priority_queue = [(0 + heuristic(start_node, end), 0, start_node)]

    while priority_queue:
        current_f, current_g, current_node = heapq.heappop(priority_queue)

        if current_node.visited:
            continue

        current_node.visited = True
        current_node.distance = current_g

        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        for neighbor in filter(None, neighbors):
            if not neighbor.visited and not neighbor.is_enemy:
                new_g = current_g + 1
                if new_g < neighbor.distance:
                    neighbor.distance = new_g
                    heapq.heappush(priority_queue, (new_g + heuristic(neighbor, end), new_g, neighbor))

    if end_node.distance == float('inf'):
        return None

    path = []
    current_node = end_node
    while current_node != start_node:
        path.append((current_node.row, current_node.col))
        neighbors = [current_node.left, current_node.right, current_node.up, current_node.down]
        valid_neighbors = [n for n in neighbors if n and not n.is_enemy]
        current_node = min(valid_neighbors, key=lambda x: x.distance)

    path.append((start_node.row, start_node.col))
    return list(reversed(path))

def add_enemies_along_path(maze, path, num_enemies):
    enemies_added = 0
    for _ in range(num_enemies):
        random_index = random.randint(1, len(path) - 2)
        row, col = path[random_index]
        if not maze[row][col].is_enemy:
            maze[row][col].is_enemy = True
            enemies_added += 1
    return enemies_added

def visualize_maze_svg(maze, path, start, end, rewards, enemies, file_name='maze_with_paths.svg'):
    cell_size = 20
    padding = 2

    dwg = svgwrite.Drawing(file_name, profile='tiny')
    dwg.viewbox(0, 0, cell_size * len(maze[0]), cell_size * len(maze))

    for row_index, row in enumerate(maze):
        for col_index, node in enumerate(row):
            x = col_index * cell_size
            y = row_index * cell_size

            if node.left is None:
                dwg.add(dwg.line((x, y), (x, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.right is None:
                dwg.add(dwg.line((x + cell_size, y), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.up is None:
                dwg.add(dwg.line((x, y), (x + cell_size, y), stroke=svgwrite.rgb(0, 0, 0, '%')))
            if node.down is None:
                dwg.add(dwg.line((x, y + cell_size), (x + cell_size, y + cell_size), stroke=svgwrite.rgb(0, 0, 0, '%')))

            if node.is_enemy:
                ghost_size = cell_size / 1.5
                ghost_x = x + cell_size / 2 - ghost_size / 2
                ghost_y = y + cell_size / 1 - ghost_size / 2
                dwg.add(dwg.text('💣', insert=(ghost_x, ghost_y), font_size=ghost_size, fill=svgwrite.rgb(120, 0, 120, '%')))

            if node.is_reward:
                dwg.add(dwg.circle(center=((x + cell_size / 2, y + cell_size / 2)),
                                   r=(cell_size - 2 * padding) / 2, fill=svgwrite.rgb(255, 255, 0, '%')))

    if path:
        for i in range(len(path) - 1):
            row1, col1 = path[i]
            row2, col2 = path[i + 1]
            x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
            x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
            dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 255, '%'), stroke_width=4))

    start_x, start_y = start[1] * cell_size + cell_size / 2, start[0] * cell_size + cell_size / 2
    end_x, end_y = end[1] * cell_size + cell_size / 2, end[0] * cell_size + cell_size / 2

    dwg.add(dwg.text('🚩', insert=(start_x - cell_size / 4, start_y - cell_size / 4),
                     font_size=cell_size / 2, fill=svgwrite.rgb(255, 0, 0, '%')))
    dwg.add(dwg.text('🏁', insert=(end_x - cell_size / 4, end_y - cell_size / 4),
                     font_size=cell_size / 2, fill=svgwrite.rgb(0, 255, 0, '%')))

    if enemies:
        for i in range(len(enemies) - 1):
            row1, col1 = enemies[i]
            row2, col2 = enemies[i + 1]
            x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
            x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
            dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 255, 0, '%'), stroke_width=4))

    for reward_location in rewards:
        print("r_loc =  ",reward_location)  # print location of rewards.
        row, col = reward_location
        x, y = col * cell_size + cell_size / 2, row * cell_size + cell_size / 2
        dwg.add(dwg.circle(center=(x, y), r=(cell_size - 2 * padding) / 2, fill=svgwrite.rgb(128, 0, 128, '%')))

    dwg.save()

def generate_a_new_maze():
    rows, cols = 30, 30  # Adjust the size of the maze as needed

    random_num_enemies = random.randint(1, 10) + 20

    print("Generating a new maze")
    random_maze = generate_random_maze(rows, cols, num_enemies=random_num_enemies, num_rewards=5)
    start_point = generate_start_on_border(rows, cols)
    end_point = generate_end_on_border(rows, cols, start_point)

    try:
        shortest_path = astar(random_maze, start_point, end_point)

        if shortest_path is not None:
            # Add two enemies randomly along the path
            enemies_added = add_enemies_along_path(random_maze, shortest_path, num_enemies=2)

            if enemies_added == 2:
                new_shortest_path = astar(random_maze, start_point, end_point)

                if new_shortest_path is not None:
                    path_stack = new_shortest_path.copy()
                    path_stack.append(start_point)
                    path_stack.append(end_point)
                    reward_locations = [(node.row, node.col) for row in random_maze for node in row if node.is_reward]
                    path_stack.extend(reward_locations)

                    print("\nStart Point:", start_point)
                    print("End Point:", end_point)
                    print("Number of Enemies:", random_num_enemies)
                    print("Shortest Path (Original):", shortest_path)
                    print("Shortest Path (Avoiding Enemies):", new_shortest_path)

                    visualize_maze_svg(random_maze, shortest_path, start_point, end_point, reward_locations, new_shortest_path,
                                        file_name='maze_with_paths.svg')

                else:
                    print("No path found after adding enemies.")
                    generate_a_new_maze()

            else:
                print("Failed to add enemies along the path.")
                generate_a_new_maze()

        else:
            print("No path found from start to end.")
            generate_a_new_maze()

    except ValueError as e:
        print("Error: " + str(e))

generate_a_new_maze()