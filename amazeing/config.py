"""Parse and validate the A-Maze-ing configuration file.

The file contains one ``KEY=VALUE`` pair per line. Empty lines and lines
starting with ``#`` are ignored. Mandatory keys are ``WIDTH``, ``HEIGHT``,
``ENTRY``, ``EXIT``, ``OUTPUT_FILE`` and ``PERFECT``; ``SEED`` is optional.
"""

from dataclasses import dataclass
from typing import Optional

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
OPTIONAL_KEYS = ("SEED",)
MAX_SIZE = 200


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


@dataclass(frozen=True)
class MazeConfig:
    """Validated maze configuration."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _parse_int(key: str, value: str) -> int:
    """Convert ``value`` to an int or raise a readable ConfigError."""
    try:
        return int(value)
    except ValueError:
        raise ConfigError(
            f"{key} must be an integer, got '{value}'"
        ) from None


def _parse_size(key: str, value: str) -> int:
    """Parse WIDTH/HEIGHT: an integer between 1 and MAX_SIZE."""
    size = _parse_int(key, value)
    if not 1 <= size <= MAX_SIZE:
        raise ConfigError(
            f"{key} must be between 1 and {MAX_SIZE}, got {size}"
        )
    return size


def _parse_coord(key: str, value: str) -> tuple[int, int]:
    """Parse a coordinate written as ``x,y``."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be in the form 'x,y', got '{value}'")
    x = _parse_int(key, parts[0].strip())
    y = _parse_int(key, parts[1].strip())
    return (x, y)


def _parse_bool(key: str, value: str) -> bool:
    """Parse ``True`` / ``False`` (case-insensitive)."""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key} must be 'True' or 'False', got '{value}'")


def read_pairs(text: str) -> dict[str, str]:
    """Split config text into a ``{KEY: VALUE}`` dict.

    Raises ConfigError on malformed lines, unknown keys or duplicates.
    """
    pairs: dict[str, str] = {}
    known = MANDATORY_KEYS + OPTIONAL_KEYS
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(
                f"line {lineno}: expected KEY=VALUE, got '{line}'"
            )
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.upper()
        if key not in known:
            raise ConfigError(f"line {lineno}: unknown key '{key}'")
        if key in pairs:
            raise ConfigError(f"line {lineno}: duplicate key '{key}'")
        if not value:
            raise ConfigError(f"line {lineno}: empty value for '{key}'")
        pairs[key] = value
    return pairs


def _check_in_bounds(
    key: str, coord: tuple[int, int], width: int, height: int
) -> None:
    """Ensure ``coord`` lies inside a ``width`` x ``height`` maze."""
    x, y = coord
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"{key} {x},{y} is outside the maze "
            f"(0..{width - 1}, 0..{height - 1})"
        )


def parse_config(text: str) -> MazeConfig:
    """Build a validated MazeConfig from the config file contents."""
    pairs = read_pairs(text)
    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")

    width = _parse_size("WIDTH", pairs["WIDTH"])
    height = _parse_size("HEIGHT", pairs["HEIGHT"])
    entry = _parse_coord("ENTRY", pairs["ENTRY"])
    exit_ = _parse_coord("EXIT", pairs["EXIT"])
    _check_in_bounds("ENTRY", entry, width, height)
    _check_in_bounds("EXIT", exit_, width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")

    seed = _parse_int("SEED", pairs["SEED"]) if "SEED" in pairs else None
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=pairs["OUTPUT_FILE"],
        perfect=_parse_bool("PERFECT", pairs["PERFECT"]),
        seed=seed,
    )


def load_config(path: str) -> MazeConfig:
    """Read and validate the configuration file at ``path``."""
    try:
        with open(path, encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        raise ConfigError(f"config file '{path}' not found") from None
    except IsADirectoryError:
        raise ConfigError(f"'{path}' is a directory") from None
    except PermissionError:
        raise ConfigError(f"permission denied: '{path}'") from None
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' is not a valid text file") from None
    except OSError as err:
        raise ConfigError(f"cannot read '{path}': {err.strerror}") from None
    return parse_config(text)
