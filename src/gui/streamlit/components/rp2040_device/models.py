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
class RP2040WriteRequest:
    request_id: str
    filename: str
    content: bytes


@dataclass(frozen=True)
class RP2040DeviceState:
    connected: bool = False
    sid_exists: bool = False
    did_exists: bool = False
    sid: str | None = None
    did: str | None = None
    filename: str | None = None
    file_size: int | None = None
    status: str = "Ready"
    error: str | None = None


@dataclass(frozen=True)
class RP2040DeviceResult:
    state: RP2040DeviceState
    transfer_complete: RP2040TransferEvent | None = None
