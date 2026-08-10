# src/main/config/app_config_loader.py

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from src.infrastructure.config.app_config_models import (
    AppRuntimeConfig,
    GoogleSheetsConfig,
    SheetSpec,
    # PathsConfig,
)


class AppConfigLoader:
    @staticmethod
    def load_from_json(path: Path, *, project_root: Path) -> AppRuntimeConfig:
        if not path.exists():
            raise FileNotFoundError(f"config.json not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            raw: Dict[str, Any] = json.load(f)

        return AppConfigLoader.parse(raw, project_root=project_root)

    @staticmethod
    def parse(raw: Dict[str, Any], *, project_root: Path) -> AppRuntimeConfig:
        # paths = AppConfigLoader._parse_paths(raw=raw, project_root=project_root)
        google_sheets = AppConfigLoader._parse_google_sheets(raw=raw)

        return AppRuntimeConfig(
            # paths=paths,
            google_sheets=google_sheets,
        )

    """
    @staticmethod
    def _parse_paths(raw: Dict[str, Any], *, project_root: Path) -> PathsConfig:
        try:
            p = raw["file_paths_local"]
        except KeyError as e:
            raise ValueError(f"Missing required config key: {e.args[0]}") from e

        if not isinstance(p, Mapping):
            raise ValueError("paths must be an object")

        file_01_rel = p.get("placeholder_csv_path")
        # if not isinstance(file_01_rel, str) or not file_01_rel.strip():
            # raise ValueError("paths.placeholder_csv_path must be a non-empty string")

        file_02_rel = p.get("placeholder_out_md")
        # if not isinstance(file_02_rel, str) or not file_02_rel.strip():
            # raise ValueError("paths.placeholder_out_json must be a non-empty string")

        return PathsConfig(
            output_dir=(project_root / file_01_rel).resolve(),
            reports_dir=(project_root / file_02_rel).resolve(),
        )
    """

    @staticmethod
    def _parse_google_sheets(raw: Dict[str, Any]) -> GoogleSheetsConfig:
        try:
            g = raw["google_sheets"]
        except KeyError as e:
            raise ValueError(f"Missing required config key: {e.args[0]}") from e

        if not isinstance(g, Mapping):
            raise ValueError("google_sheets must be an object")

        tables_raw = g.get("tables")
        if not isinstance(tables_raw, Mapping):
            raise ValueError("google_sheets.tables must be an object")

        sheets: dict[str, SheetSpec] = {}

        for key, src in tables_raw.items():
            if not isinstance(src, Mapping):
                raise ValueError(f"google_sheets.tables.{key} must be an object")

            worksheet_name = src.get("worksheet_name")
            worksheet_range = src.get("worksheet_range")
            file_name = src.get("file_name")

            if not isinstance(worksheet_name, str) or not worksheet_name.strip():
                raise ValueError(
                    f"google_sheets.tables.{key}.worksheet_name must be a non-empty string"
                )

            if not isinstance(worksheet_range, str) or not worksheet_range.strip():
                raise ValueError(
                    f"google_sheets.tables.{key}.worksheet_range must be a non-empty string"
                )

            if file_name is not None and (
                    not isinstance(file_name, str) or not file_name.strip()
            ):
                raise ValueError(
                    f"google_sheets.tables.{key}.file_name must be a non-empty string when provided"
                )

            sheets[str(key)] = SheetSpec(
                file_name=file_name.strip() if isinstance(file_name, str) else None,
                worksheet_name=worksheet_name.strip(),
                worksheet_range=worksheet_range.strip(),
            )

        return GoogleSheetsConfig(tables=sheets)
