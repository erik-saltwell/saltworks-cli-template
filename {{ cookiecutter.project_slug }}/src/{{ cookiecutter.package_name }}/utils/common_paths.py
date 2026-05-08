from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class KnownPathnames(StrEnum):
    LOGS_DIR = "logs"
    TRACE_FILE = "trace.json"
    LOG_FILE = "{{cookiecutter.package_name}}.log"


def ensure_directory(dir: Path) -> None:
    dir.mkdir(parents=True, exist_ok=True)


def working_dir() -> Path:
    """Return the path to the computed datasets directory under outputs."""
    return Path.cwd()


def logs_dir() -> Path:
    return working_dir() / KnownPathnames.LOGS_DIR


def tracefile_path() -> Path:
    return logs_dir() / KnownPathnames.TRACE_FILE
