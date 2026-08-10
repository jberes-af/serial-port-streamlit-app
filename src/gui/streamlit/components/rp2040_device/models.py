# src/gui/streamlit/components/rp2040_device/models.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RP2040Entry:
    name: str
    path: str
    is_directory: bool
    size: int | None = None


@dataclass(frozen=True)
class RP2040TransferEvent:
    filename: str
    destination: str
    size: int


@dataclass(frozen=True)
class RP2040DeviceState:
    connected: bool = False
    entries: tuple[RP2040Entry, ...] = ()
    current_directory: str = "/"

    filename: str | None = None
    file_size: int | None = None

    status: str = "Ready"
    error: str | None = None


@dataclass(frozen=True)
class RP2040DeviceResult:
    state: RP2040DeviceState
    transfer_complete: RP2040TransferEvent | None = None