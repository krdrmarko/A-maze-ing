"""Tests for amazeing.maze_io."""

from pathlib import Path

import pytest

from amazeing.maze_io import MazeData, MazeFileError, format_maze
from amazeing.maze_io import parse_maze, path_cells, read_output
from amazeing.maze_io import write_output

# 2x2 maze:   entry (0,0) -> E -> S -> exit (1,1)
#  +--+--+
#  |     |
#  +--+  +
#  |     |
#  +--+--+
SMALL = MazeData(
    grid=[[0xD, 0x3], [0xD, 0x6]],
    entry=(0, 0),
    exit=(1, 1),
    path="ES",
)


def test_format_maze() -> None:
    assert format_maze(SMALL) == "D3\nD6\n\n0,0\n1,1\nES\n"


def test_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "maze.txt"
    write_output(SMALL, str(target))
    assert read_output(str(target)) == SMALL


def test_write_to_directory(tmp_path: Path) -> None:
    with pytest.raises(MazeFileError, match="is a directory"):
        write_output(SMALL, str(tmp_path))


def test_write_to_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(MazeFileError, match="cannot write"):
        write_output(SMALL, str(tmp_path / "no" / "maze.txt"))


def test_read_missing_file(tmp_path: Path) -> None:
    with pytest.raises(MazeFileError, match="not found"):
        read_output(str(tmp_path / "missing.txt"))


@pytest.mark.parametrize(
    "text, message",
    [
        ("D7\nD7\n0,0\n1,1\nES\n", "missing empty line"),
        ("\n0,0\n1,1\nES\n", "empty grid"),
        ("D7\nD7\n\n0,0\n1,1\n", "expected entry, exit and path"),
        ("DZ\nD7\n\n0,0\n1,1\nES\n", "non-hex"),
        ("D7\nD\n\n0,0\n1,1\nES\n", "different lengths"),
        ("D7\nD7\n\n0;0\n1,1\nES\n", "invalid coordinate"),
        ("D7\nD7\n\n0,0\n1,1\nEX\n", "only contain N, E, S, W"),
    ],
)
def test_parse_errors(text: str, message: str) -> None:
    with pytest.raises(MazeFileError, match=message):
        parse_maze(text)


def test_path_cells() -> None:
    assert path_cells((0, 0), "ESWN") == [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
        (0, 0),
    ]


def test_path_cells_invalid_letter() -> None:
    with pytest.raises(ValueError):
        path_cells((0, 0), "X")


def test_dimensions() -> None:
    assert (SMALL.width, SMALL.height) == (2, 2)
