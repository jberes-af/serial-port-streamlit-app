# infrastructure/persistence/google/google_sheets/google_api_scopes.py

from typing import Literal


GoogleAccessMode = Literal["read", "write"]
DriveAccessMode = Literal["none", "read", "write", "all"]


SHEETS_SCOPES_READONLY = (
    "https://www.googleapis.com/auth/spreadsheets.readonly",
)

SHEETS_SCOPES_READ_WRITE = (
    "https://www.googleapis.com/auth/spreadsheets",
)

DRIVE_SCOPES_READONLY = (
    "https://www.googleapis.com/auth/drive.readonly",
)

DRIVE_SCOPES_FILE_WRITE = (
    "https://www.googleapis.com/auth/drive.file",
)

DRIVE_SCOPES_ALL = (
    "https://www.googleapis.com/auth/drive",
)


"""
def combined_scopes(
    *,
    sheets_mode: GoogleAccessMode,
    drive_mode: DriveAccessMode,
) -> tuple[str, ...]:
    scopes: list[str] = []

    if sheets_mode == "read":
        scopes.extend(SHEETS_SCOPES_READONLY)
    elif sheets_mode == "write":
        scopes.extend(SHEETS_SCOPES_READ_WRITE)
    else:
        raise ValueError(
            f"Unsupported Sheets mode: {sheets_mode}"
        )

    if drive_mode == "read":
        scopes.extend(DRIVE_SCOPES_READONLY)
    elif drive_mode == "write":
        scopes.extend(DRIVE_SCOPES_FILE_WRITE)
    elif drive_mode == "all":
        scopes.extend(DRIVE_SCOPES_ALL)
    elif drive_mode != "none":
        raise ValueError(
            f"Unsupported Drive mode: {drive_mode}"
        )

    return tuple(dict.fromkeys(scopes))
"""