"""Tests for amazeing.config."""

from pathlib import Path

import pytest

from amazeing.config import ConfigError, MazeConfig, load_config
from amazeing.config import parse_config

VALID = """\
# comment
WIDTH=20
HEIGHT=15

ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
"""


def make(**overrides: str) -> str:
    """Return VALID with some keys replaced (value '' removes the key)."""
    lines = []
    for line in VALID.splitlines():
        key = line.split("=", 1)[0]
        if key in overrides:
            if overrides[key]:
                lines.append(f"{key}={overrides[key]}")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def test_valid_config() -> None:
    assert parse_config(VALID) == MazeConfig(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        output_file="maze.txt",
        perfect=True,
        seed=None,
    )


def test_optional_seed_and_spaces() -> None:
    config = parse_config(make(PERFECT=" false ") + "SEED = 7\n")
    assert config.seed == 7
    assert config.perfect is False


def test_entry_with_spaces() -> None:
    assert parse_config(make(ENTRY=" 1 , 2 ")).entry == (1, 2)


def test_lowercase_key_accepted() -> None:
    assert parse_config(VALID.replace("WIDTH", "width")).width == 20


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"WIDTH": ""}, "missing mandatory key"),
        ({"WIDTH": "abc"}, "WIDTH must be an integer"),
        ({"WIDTH": "0"}, "WIDTH must be between"),
        ({"HEIGHT": "-3"}, "HEIGHT must be between"),
        ({"HEIGHT": "9999"}, "HEIGHT must be between"),
        ({"ENTRY": "1"}, "ENTRY must be in the form"),
        ({"ENTRY": "1,2,3"}, "ENTRY must be in the form"),
        ({"ENTRY": "a,b"}, "ENTRY must be an integer"),
        ({"ENTRY": "20,0"}, "outside the maze"),
        ({"EXIT": "0,-1"}, "outside the maze"),
        ({"EXIT": "0,0"}, "must be different"),
        ({"PERFECT": "yes"}, "PERFECT must be 'True' or 'False'"),
    ],
)
def test_invalid_values(overrides: dict[str, str], message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        parse_config(make(**overrides))


def test_line_without_equal() -> None:
    with pytest.raises(ConfigError, match="line 2: expected KEY=VALUE"):
        parse_config("WIDTH=3\nHEIGHT 4\n")


def test_unknown_key() -> None:
    with pytest.raises(ConfigError, match="unknown key 'COLOR'"):
        parse_config(VALID + "COLOR=red\n")


def test_duplicate_key() -> None:
    with pytest.raises(ConfigError, match="duplicate key 'WIDTH'"):
        parse_config(VALID + "WIDTH=5\n")


def test_empty_value() -> None:
    with pytest.raises(ConfigError, match="empty value for 'OUTPUT_FILE'"):
        parse_config(VALID.replace("maze.txt", ""))


def test_invalid_seed() -> None:
    with pytest.raises(ConfigError, match="SEED must be an integer"):
        parse_config(VALID + "SEED=abc\n")


def test_load_config_file(tmp_path: Path) -> None:
    path = tmp_path / "config.txt"
    path.write_text(VALID)
    assert load_config(str(path)).width == 20


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(str(tmp_path / "nope.txt"))


def test_load_directory(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="is a directory"):
        load_config(str(tmp_path))


def test_load_binary_file(tmp_path: Path) -> None:
    path = tmp_path / "bin"
    path.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(ConfigError, match="not a valid text file"):
        load_config(str(path))


def test_default_config_is_valid() -> None:
    root = Path(__file__).resolve().parent.parent
    load_config(str(root / "config.txt"))
