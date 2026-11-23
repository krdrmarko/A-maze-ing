"""Maze data container and the hexadecimal output file format.

Each cell is one hex digit whose bits mark closed walls:
bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West.
The file holds one row of digits per line, an empty line, the entry
``x,y``, the exit ``x,y`` and the shortest path as N/E/S/W letters.
"""

from dataclasses import dataclass

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# direction letter -> (dx, dy, wall bit that must be open)
MOVES: dict[str, tuple[int, int, int]] = {
    "N": (0, -1, NORTH),
    "E": (1, 0, EAST),
    "S": (0, 1, SOUTH),
    "W": (-1, 0, WEST),
}


class MazeFileError(Exception):
    """Raised when a maze file cannot be written or read."""


@dataclass
class MazeData:
    """A generated maze ready to be saved or displayed."""

    grid: list[list[int]]
    entry: tuple[int, int]
    exit: tuple[int, int]
    path: str

    @property
    def width(self) -> int:
        """Number of columns."""
        return len(self.grid[0]) if self.grid else 0

    @property
    def height(self) -> int:
        """Number of rows."""
        return len(self.grid)


def path_cells(start: tuple[int, int], path: str) -> list[tuple[int, int]]:
    """Return every cell visited when following ``path`` from ``start``."""
    x, y = start
    cells = [(x, y)]
    for letter in path:
        if letter not in MOVES:
            raise ValueError(f"invalid direction '{letter}' in path")
        dx, dy, _ = MOVES[letter]
        x, y = x + dx, y + dy
        cells.append((x, y))
    return cells


def format_maze(maze: MazeData) -> str:
    """Serialize ``maze`` to the output file format."""
    rows = ["".join(f"{cell:X}" for cell in row) for row in maze.grid]
    lines = rows + [
        "",
        f"{maze.entry[0]},{maze.entry[1]}",
        f"{maze.exit[0]},{maze.exit[1]}",
        maze.path,
    ]
    return "\n".join(lines) + "\n"


def write_output(maze: MazeData, filename: str) -> None:
    """Write ``maze`` to ``filename``."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(format_maze(maze))
    except IsADirectoryError:
        raise MazeFileError(f"'{filename}' is a directory") from None
    except PermissionError:
        raise MazeFileError(f"permission denied: '{filename}'") from None
    except OSError as err:
        raise MazeFileError(
            f"cannot write '{filename}': {err.strerror}"
        ) from None


def _parse_coord(text: str) -> tuple[int, int]:
    """Parse ``x,y`` from the output file."""
    parts = text.split(",")
    if len(parts) != 2:
        raise MazeFileError(f"invalid coordinate '{text}'")
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        raise MazeFileError(f"invalid coordinate '{text}'") from None


def parse_maze(text: str) -> MazeData:
    """Parse the output file format back into a MazeData."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    try:
        blank = lines.index("")
    except ValueError:
        raise MazeFileError("missing empty line after the grid") from None
    rows, footer = lines[:blank], lines[blank + 1:]
    if not rows:
        raise MazeFileError("empty grid")
    if len(footer) != 3:
        raise MazeFileError("expected entry, exit and path after the grid")
    try:
        grid = [[int(char, 16) for char in row] for row in rows]
    except ValueError:
        raise MazeFileError("grid contains non-hex characters") from None
    if any(len(row) != len(grid[0]) for row in grid):
        raise MazeFileError("grid rows have different lengths")
    if any(char not in MOVES for char in footer[2]):
        raise MazeFileError("path must only contain N, E, S, W")
    return MazeData(
        grid=grid,
        entry=_parse_coord(footer[0]),
        exit=_parse_coord(footer[1]),
        path=footer[2],
    )


def read_output(filename: str) -> MazeData:
    """Read a maze previously written by write_output."""
    try:
        with open(filename, encoding="utf-8") as file:
            return parse_maze(file.read())
    except FileNotFoundError:
        raise MazeFileError(f"'{filename}' not found") from None
    except PermissionError:
        raise MazeFileError(f"permission denied: '{filename}'") from None
    except (OSError, UnicodeDecodeError):
        raise MazeFileError(f"cannot read '{filename}'") from None
