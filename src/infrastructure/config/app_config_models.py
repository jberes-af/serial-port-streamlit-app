# /main/config/app_config_models.py

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class SheetSpec:
    file_name: str | None
    worksheet_name: str
    worksheet_range: str


@dataclass(frozen=True)
class GoogleSheetsConfig:
    tables: Mapping[str, SheetSpec]


"""
@dataclass(frozen=True)
class PathsConfig:
    output_dir: Path
    reports_dir: Path
"""


@dataclass(frozen=True)
class AppRuntimeConfig:
    # paths: PathsConfig
    google_sheets: GoogleSheetsConfig
