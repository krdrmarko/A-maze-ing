"""Tests for amazeing.visualizer."""

import io

from amazeing.maze_io import MazeData
from amazeing.visualizer import (
    THEMES,
    Tile,
    build_tiles,
    path_is_valid,
    render,
    run_interactive,
)

# Same 2x2 maze as in test_maze_io: (0,0) -E-> (1,0) -S-> (1,1)
SMALL = MazeData(
    grid=[[0xD, 0x3], [0xD, 0x6]],
    entry=(0, 0),
    exit=(1, 1),
    path="ES",
)

W, O, P = Tile.WALL, Tile.OPEN, Tile.PATH
EN, EX = Tile.ENTRY, Tile.EXIT


def test_tiles_without_path() -> None:
    assert build_tiles(SMALL, show_path=False) == [
        [W, W, W, W, W],
        [W, EN, O, O, W],
        [W, W, W, O, W],
        [W, O, O, EX, W],
        [W, W, W, W, W],
    ]


def test_tiles_with_path() -> None:
    assert build_tiles(SMALL, show_path=True) == [
        [W, W, W, W, W],
        [W, EN, P, P, W],
        [W, W, W, P, W],
        [W, O, O, EX, W],
        [W, W, W, W, W],
    ]


def test_full_cell_is_pattern() -> None:
    maze = MazeData(
        grid=[[0xB, 0xF, 0xE]], entry=(0, 0), exit=(2, 0), path=""
    )
    tiles = build_tiles(maze, show_path=False)
    assert tiles[1][3] == Tile.PATTERN


def test_render_plain_size() -> None:
    lines = render(SMALL, color=False).split("\n")
    assert len(lines) == 2 * SMALL.height + 1
    assert all(len(line) == 2 * (2 * SMALL.width + 1) for line in lines)
    assert lines[1] == "██EN    ██"
    assert "\033" not in "".join(lines)


def test_render_plain_path() -> None:
    assert render(SMALL, show_path=True, color=False).split("\n")[1] == (
        "██EN····██"
    )


def test_render_color_themes_differ() -> None:
    first = render(SMALL, theme=0)
    second = render(SMALL, theme=1)
    assert "\033[" in first
    assert first != second
    assert render(SMALL, theme=len(THEMES)) == first


def test_path_is_valid() -> None:
    assert path_is_valid(SMALL)
    assert not path_is_valid(
        MazeData(SMALL.grid, SMALL.entry, SMALL.exit, "SE")
    )
    assert not path_is_valid(
        MazeData(SMALL.grid, SMALL.entry, SMALL.exit, "E")
    )


def run_with(choices: list[str], regenerate_result: MazeData) -> str:
    """Drive run_interactive with scripted input and return its output."""
    answers = iter(choices)
    out = io.StringIO()
    run_interactive(
        SMALL,
        lambda: regenerate_result,
        color=False,
        input_fn=lambda _prompt: next(answers),
        out=out,
    )
    return out.getvalue()


def test_interactive_toggle_path_and_quit() -> None:
    output = run_with(["2", "4"], SMALL)
    assert "··" in output
    assert "1. Re-generate" in output


def test_interactive_invalid_choice() -> None:
    assert "Invalid choice 'x'" in run_with(["x", "4"], SMALL)


def test_interactive_theme() -> None:
    assert f"Theme: {THEMES[1][0]}" in run_with(["3", "4"], SMALL)


def test_interactive_regenerate() -> None:
    other = MazeData(
        grid=[[0xD, 0x7]], entry=(0, 0), exit=(1, 0), path="E"
    )
    output = run_with(["1", "4"], other)
    assert "██EN  EX██" in output


def test_interactive_regenerate_error() -> None:
    def broken() -> MazeData:
        raise ValueError("boom")

    out = io.StringIO()
    answers = iter(["1", "4"])
    run_interactive(
        SMALL,
        broken,
        color=False,
        input_fn=lambda _prompt: next(answers),
        out=out,
    )
    assert "Error: boom" in out.getvalue()


def test_interactive_eof() -> None:
    def eof(_prompt: str) -> str:
        raise EOFError

    run_interactive(SMALL, lambda: SMALL, color=False, input_fn=eof,
                    out=io.StringIO())
