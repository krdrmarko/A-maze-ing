import random
from collections import deque

config = {
    "width": 10,
    "height": 10,
    "start": (0, 0),
    "finish": (9, 9),
    "seed": 42,
    "perfect": True,
}


class MazeGenerator:
    def __init__(self, config: dict):
        self.width = config["width"]
        self.height = config["height"]
        self.start = config["start"]
        self.finish = config["finish"]
        self.seed = config["seed"]
        self.perfect = config["perfect"]

        # def generate_maze(config: dict) -> list[list[int]]:
        #     width = config["width"]
        #     height = config["height"]
        #     start = config["start"]
        #     finish = config["finish"]
        #     seed = config["seed"]
        #     perfect = config["perfect"]

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Invalid dimentions")
        if not (
            0 <= self.start[0] < self.width
            and 0 <= self.start[1] < self.height
        ):
            raise ValueError("Invalid start coordinates")
        if not (
            0 <= self.finish[0] < self.width
            and 0 <= self.finish[1] < self.height
        ):
            raise ValueError("Invalid finish coordinates")
        if self.start == self.finish:
            raise ValueError("Start and finish must be different")

        # Random generator
        self.rng = random.Random(self.seed)

        # Generate maze with 2 walls
        self.maze = [
            [1] * (self.width * 3) for _ in range(self.height * 3)
        ]  # because wall+cell+wall setback check the last

        # shift in relation to the location
        self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        self.visited = set()

        self.tree_edges = set()
        # Create pattern 42 if maze is large enought
        self.pattern = set()

    def is_valid_opening(self, x, y, nx, ny):
        dx = nx - x
        dy = ny - y
        # Physical coordinates of the two walls
        positions = []
        for i in range(1, 3):
            px = x * 3 + 1 + dx * i
            py = y * 3 + 1 + dy * i
            positions.append((py, px))

        # cell center
        positions.append((ny * 3 + 1, nx * 3 + 1))
        # save original values
        original = [self.maze[py][px] for py, px in positions]

        # Temporary open the passage

        for py, px in positions:
            self.maze[py][px] = 0
        valid = True
        # check all physical 3x3 areas
        for col in range(len(self.maze[0])):
            consecutive = 0
            for row in range(len(self.maze)):
                if self.maze[row][col] == 0:
                    consecutive += 1
                    if consecutive > 4:
                        valid = False
                        break
                else:
                    consecutive = 0
            if not valid:
                break
        # Restore the original walls
        for (py, px), value in zip(positions, original):
            self.maze[py][px] = value
        return valid

    def open_passage(self, x, y, nx, ny):
        dx = nx - x
        dy = ny - y

        for i in range(1, 3):
            self.maze[y * 3 + 1 + dy * i][x * 3 + 1 + dx * i] = 0
        self.maze[ny * 3 + 1][nx * 3 + 1] = 0

    def create_pattern(self):
        if self.width >= 7 and self.height >= 5:
            digits = ["#...###", "#.....#", "###.###", "..#.#..", "..#.###"]
            protected_cells = {
                (0, 0),
                (self.width - 1, 0),
                (0, self.height - 1),
                (self.width - 1, self.height - 1),
                (self.width // 2, self.height // 2),
                self.start,
                self.finish,
            }
            # Finding best location
            best_pattern = None
            best_distance = None

            center_x = (self.width - 7) // 2  # for make it in center
            center_y = (self.height - 5) // 2
            for offset_y in range(self.height - 4):
                for offset_x in range(self.width - 6):
                    candidate = set()
                    for y, row in enumerate(digits):
                        for x, cell in enumerate(row):
                            if cell == "#":
                                candidate.add((x + offset_x, y + offset_y))
                    if candidate & protected_cells:
                        continue
                    distance = abs(offset_x - center_x) + abs(
                        offset_y - center_y
                    )
                    if best_distance is None or distance < best_distance:
                        best_distance = distance
                        best_pattern = candidate
            if best_pattern is None:
                print(
                    "Error: can not place pattern 42 without blocking required cells"
                )
                pattern = set()

            else:
                self.pattern = best_pattern
        else:
            print("Error: maze is too small for pattern 42")
            pattern = set()

        # Iterative DFS

    def cut_maze(self, origin_cell):

        stack = [origin_cell]  # for visited, but can continue
        # already checked cells and restricted
        x, y = origin_cell
        # first cell
        self.maze[y * 3 + 1][x * 3 + 1] = 0
        self.visited.add(origin_cell)
        while stack:  # while stack is not Null
            x, y = stack[-1]  # current position of DFS
            neighbors = self.directions.copy()  # create a list
            self.rng.shuffle(neighbors)  # mix the list
            found = False
            for dx, dy in neighbors:  # dx,dy - cmesheniya
                nx = x + dx  # neighbor coordinates
                ny = y + dy
                neighbor = (nx, ny)
                if not (
                    0 <= nx < self.width and 0 <= ny < self.height
                ):  # if the neighbor is outside maze, skip it
                    continue
                if neighbor in self.visited:  # if already visited, skip
                    continue
                if neighbor in self.pattern:
                    continue
                if not self.is_valid_opening(x, y, nx, ny):
                    continue
                self.open_passage(x, y, nx, ny)
                edge = tuple(sorted(((x, y), neighbor)))

                # #Open 2 positions between cells
                # for i in range(1,3):
                #     maze[y*3+1+dy*i][x*3+1+dx*i]=0
                # maze[ny*3+1][nx*3+1]=0
                # edge =tuple(sorted(((x,y),neighbor)))
                self.tree_edges.add(edge)
                self.visited.add(neighbor)
                stack.append(neighbor)
                found = True
                break
            if not found:
                stack.pop()
        # Generate all accessible cells

    def add_extra_passages(self):
        possible_edges = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern:
                    continue
                for dx, dy in [(1, 0), (0, 1)]:
                    nx = x + dx
                    ny = y + dy
                    neighbor = (nx, ny)
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                    if (x, y) not in self.visited:
                        continue
                    edge = tuple(sorted(((x, y), neighbor)))
                    if edge in self.tree_edges:
                        continue
                    possible_edges.append(edge)
                    self.rng.shuffle(possible_edges)
                    opened = 0
                    for edge in possible_edges:
                        if opened >= 2:
                            break
                        (x1, y1), (x2, y2) = edge
                        self.open_passage(x1, y1, x2, y2)
                        opened += 1
                    if opened < 2:
                        raise ValueError("Cannot create two additional pages")

    def generate(self):
        self.create_pattern()

        # start DFS from entry cell
        self.cut_maze(self.start)
        # visit any remaining accessible cells
        for y in range(self.height):
            for x in range(self.width):
                cell = (x, y)
                if cell not in self.visited and cell not in self.pattern:
                    self.cut_maze(cell)
        if not self.perfect:
            self.add_extra_passages()
        return self.maze

        # Add additional ways if maze is not perfect
        # if not perfect:
        #     possible_edges = []
        #     for y in range(height):
        #         for x in range(width):
        #             if (x,y) in pattern:
        #                 continue
        #             for dx,dy in [(1,0),(0,1)]: #to check bottom and right
        #                 nx = x+dx
        #                 ny= y+ dy
        #                 neighbor=(nx,ny)
        #                 if not (0<=nx<width and 0<=ny<height):
        #                     continue
        #                 if neighbor in pattern:
        #                     continue
        #                 edge= tuple(sorted(((x,y),neighbor))) #additional way
        #                 if edge in tree_edges:
        #                     continue
        #                 possible_edges.append(edge)
        #     rng.shuffle(possible_edges)
        #     if len(possible_edges)<2:
        #         raise ValueError ("Not enough possible edges to create two loops")
        #     extra_edges=possible_edges[:2]
        #     for edge in possible_edges:
        #         (x1,y1),(x2,y2)=edge
        #         if is_valid_opening(maze,x1,y1,x2,y2):
        #             dx=x2-x1
        #             dy=y2-y1
        #             for i in range(1,3):
        #                 maze[y1*3+1+dy*i][x1*3+1+dx*i]=0
        # return maze

    def convert_to_hex(self):
        result = []

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                value = 0
                # check North
                if self.maze[y * 3][x * 3 + 1] == 1:
                    value |= 1
                    # check East
                if self.maze[y * 3 + 1][x * 3 + 2] == 1:
                    value |= 2
                    # check South
                if self.maze[y * 3 + 2][x * 3 + 1] == 1:
                    value |= 4
                    # check West
                if self.maze[y * 3 + 1][x * 3] == 1:
                    value |= 8
                row += format(value, "X")
            result.append(row)
        return result

    def path_todirections(self, path):
        directions = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}
        result = ""
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            result += directions[(dx, dy)]
        return result

    def save_maze(self, filename, path):
        hex_maze = self.convert_to_hex()
        directions = self.path_todirections(path)
        with open(filename, "w") as file:
            for row in hex_maze:
                file.write(row + "\n")
            file.write("\n")
            file.write(f"{self.start[0]},{self.start[1]}\n")
            file.write(f"{self.finish[0]},{self.finish[1]}\n")
            file.write(directions + "\n")

    def bfs(self):
        start = self.start
        finish = self.finish
        if self.maze[start[1] * 3 + 1][start[0] * 3 + 1] == 1:
            return None
        if self.maze[finish[1] * 3 + 1][finish[0] * 3 + 1] == 1:
            return None
        height = len(self.maze) // 3
        width = len(self.maze[0]) // 3
        if start == finish:
            return [start]
        queue = deque([start])
        visited_BFS = {start}

        parent = {}
        while queue:
            x, y = queue.popleft()
            if (x, y) == finish:
                break
            for dx, dy in self.directions:
                nx = x + dx
                ny = y + dy

                neighbor = (nx, ny)

                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if neighbor in visited_BFS:
                    continue

                # check for physical center of neighbor
                if self.maze[ny * 3 + 1][nx * 3 + 1] == 1:
                    continue
                # check the first physical position
                if self.maze[y * 3 + 1 + dy][x * 3 + 1 + dx] == 1:
                    continue
                # check the second physical position
                if self.maze[y * 3 + 1 + dy * 2][x * 3 + 1 + dx * 2] == 1:
                    continue
                visited_BFS.add(neighbor)
                parent[neighbor] = (x, y)

                queue.append(neighbor)

        if finish not in visited_BFS:
            return None

        # return the path
        path = []
        current = finish

        while current != start:
            path.append(current)
            current = parent[current]

        path.append(start)
        path.reverse()

        return path


generator = MazeGenerator(config)
maze = generator.generate()
path = generator.bfs()

if path is not None:
    generator.save_maze("maze.txt", path)
else:
    print("No path found")
