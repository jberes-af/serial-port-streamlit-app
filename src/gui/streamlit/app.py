# src/gui/streamlit/app.py

from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))



from src.gui.streamlit.screens.main_page import render_main_page

from src.main.composition_root import (
    AppContainer,
    build_app_container,
)

_APP_NAME = "Wedge - Sensor Pairing App"

import streamlit as st


def run_app() -> None:
    st.set_page_config(
        page_title=_APP_NAME,
        page_icon=":material/settings_ethernet:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    container: AppContainer = build_app_container()

    render_main_page(container)


if __name__ == "__main__":
    run_app()
