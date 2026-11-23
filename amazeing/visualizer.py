"""Terminal (ASCII / ANSI color) rendering of a maze.

A ``W`` x ``H`` maze is drawn on a ``(2W+1)`` x ``(2H+1)`` tile grid:
odd/odd tiles are cells, the tiles between them are walls or passages.
Each tile is printed two characters wide so the maze looks square.
"""

import sys
from enum import Enum
from typing import Callable, Optional, TextIO

from amazeing.maze_io import EAST, MOVES, NORTH, SOUTH, WEST, MazeData

FULL_CELL = NORTH | EAST | SOUTH | WEST


class Tile(Enum):
    """Kinds of tiles in the rendered picture."""

    WALL = "wall"
    OPEN = "open"
    PATTERN = "pattern"
    PATH = "path"
    ENTRY = "entry"
    EXIT = "exit"


# Characters used when colors are disabled.
PLAIN: dict[Tile, str] = {
    Tile.WALL: "██",
    Tile.OPEN: "  ",
    Tile.PATTERN: "▒▒",
    Tile.PATH: "··",
    Tile.ENTRY: "EN",
    Tile.EXIT: "EX",
}

RESET = "\033[0m"

# Color themes: (wall, pattern) ANSI 256-color background codes.
THEMES: list[tuple[str, int, int]] = [
    ("white", 255, 244),
    ("blue", 27, 51),
    ("green", 34, 190),
    ("orange", 208, 196),
    ("purple", 93, 213),
]
PATH_COLOR = 220
ENTRY_COLOR = 46
EXIT_COLOR = 196


def _bg(code: int) -> str:
    """Two spaces with an ANSI 256-color background."""
    return f"\033[48;5;{code}m  {RESET}"


def build_tiles(maze: MazeData, show_path: bool) -> list[list[Tile]]:
    """Convert the hex grid into a 2D list of tiles."""
    width, height = maze.width, maze.height
    tiles = [[Tile.WALL] * (2 * width + 1) for _ in range(2 * height + 1)]

    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            ty, tx = 2 * y + 1, 2 * x + 1
            if cell == FULL_CELL:
                tiles[ty][tx] = Tile.PATTERN
                continue
            tiles[ty][tx] = Tile.OPEN
            if not cell & NORTH:
                tiles[ty - 1][tx] = Tile.OPEN
            if not cell & SOUTH:
                tiles[ty + 1][tx] = Tile.OPEN
            if not cell & WEST:
                tiles[ty][tx - 1] = Tile.OPEN
            if not cell & EAST:
                tiles[ty][tx + 1] = Tile.OPEN

    if show_path:
        x, y = maze.entry
        for letter in maze.path:
            dx, dy, _ = MOVES[letter]
            tiles[2 * y + 1 + dy][2 * x + 1 + dx] = Tile.PATH
            x, y = x + dx, y + dy
            tiles[2 * y + 1][2 * x + 1] = Tile.PATH

    ex, ey = maze.entry
    tiles[2 * ey + 1][2 * ex + 1] = Tile.ENTRY
    xx, xy = maze.exit
    tiles[2 * xy + 1][2 * xx + 1] = Tile.EXIT
    return tiles


def render(
    maze: MazeData,
    show_path: bool = False,
    theme: int = 0,
    color: bool = True,
) -> str:
    """Return the maze as a printable string.

    ``theme`` indexes THEMES (wraps around). With ``color=False`` plain
    characters from PLAIN are used instead of ANSI escape codes.
    """
    tiles = build_tiles(maze, show_path)
    if color:
        _, wall, pattern = THEMES[theme % len(THEMES)]
        palette = {
            Tile.WALL: _bg(wall),
            Tile.OPEN: "  ",
            Tile.PATTERN: _bg(pattern),
            Tile.PATH: _bg(PATH_COLOR),
            Tile.ENTRY: _bg(ENTRY_COLOR),
            Tile.EXIT: _bg(EXIT_COLOR),
        }
    else:
        palette = PLAIN
    return "\n".join(
        "".join(palette[tile] for tile in row) for row in tiles
    )


MENU = (
    "=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Quit"
)


def run_interactive(
    maze: MazeData,
    regenerate: Callable[[], MazeData],
    color: bool = True,
    input_fn: Callable[[str], str] = input,
    out: Optional[TextIO] = None,
) -> None:
    """Display ``maze`` and react to user choices until they quit.

    ``regenerate`` is called to build a new maze (option 1); it may raise
    an Exception, whose message is shown without leaving the loop.
    """
    stream = out if out is not None else sys.stdout
    show_path = False
    theme = 0
    message = ""
    while True:
        if color:
            stream.write("\033[2J\033[H")
        stream.write(render(maze, show_path, theme, color) + "\n\n")
        if message:
            stream.write(message + "\n")
            message = ""
        stream.write(MENU + "\n")
        stream.flush()
        try:
            choice = input_fn("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            stream.write("\n")
            return
        if choice == "1":
            try:
                maze = regenerate()
            except Exception as err:
                message = f"Error: {err}"
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            theme = (theme + 1) % len(THEMES)
            message = f"Theme: {THEMES[theme][0]}"
        elif choice == "4":
            return
        else:
            message = f"Invalid choice '{choice}', please enter 1-4."


def path_is_valid(maze: MazeData) -> bool:
    """Check that the path stays inside the maze and never crosses a wall.

    Useful to sanity-check a maze before displaying it.
    """
    x, y = maze.entry
    for letter in maze.path:
        dx, dy, bit = MOVES[letter]
        if maze.grid[y][x] & bit:
            return False
        x, y = x + dx, y + dy
        if not (0 <= x < maze.width and 0 <= y < maze.height):
            return False
    return (x, y) == maze.exit
