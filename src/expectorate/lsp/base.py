from dataclasses import dataclass
from logging import Logger
from pathlib import Path


@dataclass
class Base:
    workdir: Path
    output: Path
    log: Logger
