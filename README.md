*This project has been created as part of the 42 curriculum by makrivor, ysekioka.*

# A-Maze-ing

## Description

A-Maze-ing generates a random maze from a configuration file, writes it to
a file using a hexadecimal wall encoding, and displays it in the terminal
with the shortest path from the entry to the exit. Cells of the maze form a
"42" pattern when the maze is large enough.

The maze generation logic lives in the reusable `mazegen` package, which can
be installed on its own (`mazegen-*.whl` / `mazegen-*.tar.gz`).

## Instructions

Requirements: Python 3.10 or later. The program itself has no third-party
dependencies.

```sh
make install          # create .venv and install dev tools (flake8, mypy, pytest, build)
make run              # python3 a_maze_ing.py config.txt
make run CONFIG=my.txt
make debug            # run under pdb
make test             # pytest
make lint             # flake8 + mypy (required flags)
make lint-strict      # flake8 + mypy --strict
make package          # build mazegen-*.whl and mazegen-*.tar.gz at the repo root
make clean            # remove __pycache__, .mypy_cache, .pytest_cache, build files
make fclean           # clean + remove .venv
```

Or directly:

```sh
python3 a_maze_ing.py config.txt
```

### Interactive menu

```
1. Re-generate a new maze      (new random seed, output file is rewritten)
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
```

Colors are used when the output is a terminal. Entry is green, exit red, the
path yellow, and the "42" cells use a separate color in each theme.

## Configuration file

One `KEY=VALUE` per line. Empty lines and lines starting with `#` are
ignored. Keys are case-insensitive; spaces around `=` are allowed.

| Key           | Required | Format              | Example     |
|---------------|----------|---------------------|-------------|
| `WIDTH`       | yes      | integer, 1–200      | `WIDTH=20`  |
| `HEIGHT`      | yes      | integer, 1–200      | `HEIGHT=15` |
| `ENTRY`       | yes      | `x,y` inside maze   | `ENTRY=0,0` |
| `EXIT`        | yes      | `x,y`, ≠ `ENTRY`    | `EXIT=19,14`|
| `OUTPUT_FILE` | yes      | file path           | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | yes      | `True` / `False`    | `PERFECT=True` |
| `SEED`        | no       | integer             | `SEED=42`   |

The program stops with a clear `Error: ...` message (and exit status 1) for
a missing/unreadable file, malformed lines, unknown or duplicate keys,
missing mandatory keys, non-numeric values, out-of-range sizes, coordinates
outside the maze, or identical entry and exit.

A default `config.txt` is provided at the root of the repository.

### Output file format

One hex digit per cell, one row per line. Bits set mean a closed wall:
bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West. After the grid
comes an empty line, the entry `x,y`, the exit `x,y`, and the shortest path
as a string of `N`, `E`, `S`, `W`.

## Maze generation algorithm

<!-- TODO (makrivor): describe and justify the algorithm. -->
Iterative depth-first search (recursive backtracker) with a seeded random
generator. When `PERFECT=False`, extra passages are opened to create loops.
The shortest path is computed with breadth-first search.

## Reusable code

The `mazegen` package (`mazegen/`) is the reusable part:

```python
from mazegen import MazeGenerator

gen = MazeGenerator({"width": 20, "height": 15, "start": (0, 0),
                     "finish": (19, 14), "seed": 42, "perfect": True})
gen.generate()
rows = gen.convert_to_hex()   # list of hex strings, one per row
cells = gen.bfs()             # shortest path as a list of (x, y)
print(gen.path_todirections(cells))
```

Install it with `pip install mazegen-1.0.0-py3-none-any.whl`.

The `amazeing/` package (config parsing, output file, terminal display) is
specific to this program and is not shipped in the package.

## Team and project management


makrivor | Maze generation (`mazegen`): algorithm, "42" pattern, perfect/imperfect mazes, shortest path
ysekioka | I/O and tooling: config parsing and validation, terminal display, Makefile, lint, tests, packaging, README/LICENSE

<!-- TODO: planning, what worked, what could be improved, tools used. -->

## Resources

- [Maze generation algorithms – Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Breadth-first search – Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python Packaging User Guide](https://packaging.python.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Use of AI

AI was used to help brainstorm algorithm ideas, check basic Python syntax, run test cases, and pick up ideas for parts of the I/O code (config parser, visualizer, Makefile, tests), which we then reviewed and tested.
