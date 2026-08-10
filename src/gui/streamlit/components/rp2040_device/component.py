# /src/gui/streamlit/components/rp2040_device/component.py

import streamlit as st

from src.gui.streamlit.components.rp2040_device.frontend.ui_css import (
    CSS,
)
from src.gui.streamlit.components.rp2040_device.frontend.ui_html import (
    HTML,
)
from src.gui.streamlit.components.rp2040_device.frontend.ui_java_script import (
    JS,
)
from src.gui.streamlit.components.rp2040_device.models import (
    RP2040DeviceResult,
    RP2040DeviceState,
    RP2040Entry,
    RP2040TransferEvent,
)

rp2040_device_component = st.components.v2.component(
    name="rp2040_device",
    html=HTML,
    css=CSS,
    js=JS,
)


def render_rp2040_device(
        *,
        baud_rate: int = 115_200,
        destination: str = "/",
        timeout_ms: int = 5_000,
        key: str = "rp2040_device",
) -> RP2040DeviceResult:
    result = rp2040_device_component(
        data={
            "baudRate": baud_rate,
            "destination": destination,
            "timeoutMs": timeout_ms,
        },
        default={
            "connected": False,
            "entries": [],
            "current_directory": destination,
            "filename": None,
            "file_size": None,
            "status": "Ready",
            "error": None,
        },
        on_connected_change=lambda: None,
        on_entries_change=lambda: None,
        on_current_directory_change=lambda: None,
        on_filename_change=lambda: None,
        on_file_size_change=lambda: None,
        on_status_change=lambda: None,
        on_error_change=lambda: None,
        on_transfer_complete_change=lambda: None,
        key=key,
        height=600,
    )

    entries = tuple(
        RP2040Entry(
            name=item["name"],
            path=item["path"],
            is_directory=item["isDirectory"],
            size=item.get("size"),
        )
        for item in result.entries
    )

    transfer_event = None

    if result.transfer_complete:
        transfer_event = (
            RP2040TransferEvent(
                filename=(
                    result.transfer_complete[
                        "filename"
                    ]
                ),
                destination=(
                    result.transfer_complete[
                        "destination"
                    ]
                ),
                size=(
                    result.transfer_complete[
                        "size"
                    ]
                ),
            )
        )

    state = RP2040DeviceState(
        connected=result.connected,
        entries=entries,
        current_directory=(
            result.current_directory
        ),
        filename=result.filename,
        file_size=result.file_size,
        status=result.status,
        error=result.error,
    )

    return RP2040DeviceResult(
        state=state,
        transfer_complete=transfer_event,
    )
