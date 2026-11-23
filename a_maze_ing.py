"""A-Maze-ing entry point.

Usage: python3 a_maze_ing.py config.txt
"""

import random
import sys
from typing import Optional

from amazeing.config import ConfigError, MazeConfig, load_config
from amazeing.maze_io import MazeData, MazeFileError, write_output
from amazeing.visualizer import run_interactive
from mazegen import MazeGenerator


class GenerationError(Exception):
    """Raised when the generator cannot produce a usable maze."""


def build_maze(config: MazeConfig, seed: Optional[int]) -> MazeData:
    """Run the generator and convert its result into a MazeData."""
    try:
        generator = MazeGenerator(
            {
                "width": config.width,
                "height": config.height,
                "start": config.entry,
                "finish": config.exit,
                "seed": seed,
                "perfect": config.perfect,
            }
        )
        generator.generate()
        cells = generator.bfs()
    except (ValueError, IndexError, KeyError) as err:
        raise GenerationError(str(err)) from None
    if cells is None:
        raise GenerationError("no path between ENTRY and EXIT")
    hex_rows = generator.convert_to_hex()
    grid = [[int(char, 16) for char in row] for row in hex_rows]
    return MazeData(
        grid=grid,
        entry=config.entry,
        exit=config.exit,
        path=generator.path_todirections(cells),
    )


def main(argv: list[str]) -> int:
    """Parse arguments, generate, save and display the maze."""
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        return 1
    try:
        config = load_config(argv[1])
        maze = build_maze(config, config.seed)
        write_output(maze, config.output_file)
    except (ConfigError, GenerationError, MazeFileError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    def regenerate() -> MazeData:
        """Build a fresh maze with a random seed and save it."""
        new_maze = build_maze(config, random.randrange(2**32))
        write_output(new_maze, config.output_file)
        return new_maze

    run_interactive(maze, regenerate, color=sys.stdout.isatty())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
