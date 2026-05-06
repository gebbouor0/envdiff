"""envdiff — Compare .env files across environments."""

__version__ = "0.1.0"
__all__ = ["parse_env_file", "diff_env_files"]

from envdiff.parser import parse_env_file


def diff_env_files(file_a: str, file_b: str) -> dict:
    """Compare two .env files and return a diff summary.

    Args:
        file_a: Path to the first .env file.
        file_b: Path to the second .env file.

    Returns:
        A dict with keys 'only_in_a', 'only_in_b', and 'changed',
        each containing a list of variable names.
    """
    env_a = parse_env_file(file_a)
    env_b = parse_env_file(file_b)

    keys_a = set(env_a)
    keys_b = set(env_b)

    return {
        "only_in_a": sorted(keys_a - keys_b),
        "only_in_b": sorted(keys_b - keys_a),
        "changed": sorted(
            key for key in keys_a & keys_b if env_a[key] != env_b[key]
        ),
    }
