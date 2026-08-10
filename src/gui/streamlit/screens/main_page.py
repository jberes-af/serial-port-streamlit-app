# src/gui/streamlit/screens/main_page.py

import streamlit as st

from src.gui.streamlit.components.rp2040_device.component import (
    render_rp2040_device,
)
from src.main.composition_root import AppContainer


def render_main_page(
        app: AppContainer,
) -> None:
    st.write(
        "Connect an RP2040, browse its filesystem, "
        "and upload a local file directly from this browser."
    )

    result = render_rp2040_device(
        baud_rate=115_200,
        destination="/",
        key="rp2040_device",
    )

    if result.state.error:
        st.error(
            result.state.error
        )

    if result.transfer_complete:
        event = result.transfer_complete

        st.success(
            f"Uploaded {event.filename} "
            f"to {event.destination}"
        )
