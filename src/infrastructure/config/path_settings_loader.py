# /src/infrastructure/config/path_settings_loader.py

from pathlib import Path


class SettingsError(RuntimeError):
    pass


def resolve_config_path(project_root: Path) -> Path:
    config_path = (project_root / "config" / "config.json").resolve()

    if not config_path.exists() or not config_path.is_file():
        raise SettingsError(f"App config JSON not found: {config_path}")

    return config_path


"""
def resolve_state_dir(project_root: Path) -> Path:
    state_dir = (project_root / "state").resolve()
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def resolve_secret_file(
    *,
    project_root: Path,
    filename: str | None,
) -> Path | None:
    if not filename:
        return None

    path = (project_root / "secrets" / filename).resolve()
    return path
"""
