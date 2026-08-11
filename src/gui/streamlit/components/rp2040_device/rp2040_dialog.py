# /src/gui/streamlit/components/rp2040_device/rp2040_dialog.py

from src.gui.streamlit.components.rp2040_device.frontend.ui_css import CSS
from src.gui.streamlit.components.rp2040_device.frontend.ui_html import HTML
from src.gui.streamlit.components.rp2040_device.frontend.ui_java_script import JS
from src.gui.streamlit.components.rp2040_device.models import (
    RP2040DeviceResult,
    RP2040DeviceState,
    RP2040TransferEvent,
    RP2040WriteRequest,
)

import base64
import streamlit as st

rp2040_device_component = st.components.v2.component(
    name="rp2040_device",
    html=HTML,
    css=CSS,
    js=JS,
)


def render_rp2040_device(
        *,
        baud_rate: int = 115_200,
        write_request: RP2040WriteRequest | None = None,
        key: str = "rp2040_device",
) -> RP2040DeviceResult:
    """Render the browser-side RP2040 Web Serial component."""

    write_data: dict[str, str] | None = None

    if write_request is not None:
        write_data = {
            "filename": write_request.filename,
            "contentBase64": base64.b64encode(
                write_request.content
            ).decode("ascii"),
        }

    result = rp2040_device_component(
        data={
            "baudRate": baud_rate,
            "timeoutMs": 5_000,
            "writeRequest": write_data,
        },
        default={
            "connected": False,
            "sid_exists": False,
            "did_exists": False,
            "sid": None,
            "did": None,
            "status": "Ready",
            "error": None,
        },
        on_connected_change=lambda: None,
        on_sid_exists_change=lambda: None,
        on_did_exists_change=lambda: None,
        on_sid_change=lambda: None,
        on_did_change=lambda: None,
        on_status_change=lambda: None,
        on_error_change=lambda: None,
        on_transfer_complete_change=lambda: None,
        key=key,
        height=150,
    )

    transfer_event: RP2040TransferEvent | None = None

    if result.transfer_complete:
        transfer_event = RP2040TransferEvent(
            filename=result.transfer_complete["filename"],
            destination=result.transfer_complete["destination"],
            size=result.transfer_complete["size"],
        )

    state = RP2040DeviceState(
        connected=result.connected,
        sid_exists=result.sid_exists,
        did_exists=result.did_exists,
        sid=result.sid,
        did=result.did,
        status=result.status,
        error=result.error,
    )

    return RP2040DeviceResult(
        state=state,
        transfer_complete=transfer_event,
    )
