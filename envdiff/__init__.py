"""envdiff — Compare .env files across environments."""

__version__ = "0.1.0"
__all__ = ["parse_env_file"]

from envdiff.parser import parse_env_file
