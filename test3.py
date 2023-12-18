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
        print("generate random maze")

        return maze

    def generate_start_on_border(rows, cols):
        print("maze border start")
        return (random.randint(1, rows - 2), 0)


    def generate_end_on_border(rows, cols, start):
        print("maze end border")
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
            return MazeNode.generate_end_on_border(rows, cols, start)



    def visualize_maze_svg(maze, original_path, new_path, start, end, rewards, enemies, file_name='maze.svg'):
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

        if original_path:
            for i in range(len(original_path) - 1):
                row1, col1 = original_path[i]
                row2, col2 = original_path[i + 1]
                x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
                x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
                dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 255, '%'), stroke_width=4))

        if new_path:
            for i in range(len(new_path) - 1):
                row1, col1 = new_path[i]
                row2, col2 = new_path[i + 1]
                x1, y1 = col1 * cell_size + cell_size / 2, row1 * cell_size + cell_size / 2
                x2, y2 = col2 * cell_size + cell_size / 2, row2 * cell_size + cell_size / 2
                dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 255, 0, '%'), stroke_width=4))

        start_x, start_y = start[1] * cell_size + cell_size / 2, start[0] * cell_size + cell_size / 2
        end_x, end_y = end[1] * cell_size + cell_size / 2, end[0] * cell_size + cell_size / 2

        dwg.add(dwg.text('🚩', insert=(start_x - cell_size / 4, start_y - cell_size / 4),
                         font_size=cell_size / 2, fill=svgwrite.rgb(255, 0, 0, '%')))
        dwg.add(dwg.text('🏁', insert=(end_x - cell_size / 4, end_y - cell_size / 4),
                         font_size=cell_size / 2, fill=svgwrite.rgb(0, 255, 0, '%')))

        for reward_location in rewards:
            row, col = reward_location
            x, y = col * cell_size + cell_size / 2, row * cell_size + cell_size / 2
            dwg.add(dwg.circle(center=(x, y), r=(cell_size - 2 * padding) / 2, fill=svgwrite.rgb(128, 0, 128, '%')))

        dwg.save()

# Example usage
rows, cols = 40, 40

random_num_enemies = random.randint(1, 10) + 30
random_num_rewards = random.randint(1, 10) + 40

random_maze = MazeNode.generate_random_maze(rows, cols, num_enemies=random_num_enemies, num_rewards=random_num_rewards)
start_point = MazeNode.generate_start_on_border(rows, cols)
end_point = MazeNode.generate_end_on_border(rows, cols, start_point)

# to store and view generated maze.
MazeNode.visualize_maze_svg(random_maze, [], [], start_point, end_point, [], [], file_name='maze.svg')
MazeNode.visualize_maze_svg(random_maze, [], [], start_point, end_point, [], [], file_name='maze.img')
