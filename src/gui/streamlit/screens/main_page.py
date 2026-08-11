# src/gui/streamlit/screens/main_page.py

from uuid import uuid4

from src.gui.streamlit.components.rp2040_device.rp2040_dialog import (
    render_rp2040_device,
)
from src.gui.streamlit.components.rp2040_device.models import (
    RP2040DeviceState,
    RP2040WriteRequest,
    RP2040DeviceResult,
)
from src.main.composition_root import AppContainer

import json
import streamlit as st

NEW_SENSOR_IDS_KEY = "new_sensor_ids"
SENSOR_ID_INPUT_KEY = "sensor_id_input"

_SENSOR_ID_LENGTH = 5


def render_main_page(
        app_name: str,
        app: AppContainer,
) -> None:
    _initialize_session_state()

    st.title(app_name)

    st.subheader("Connect a Wedge")

    st.write("")


    write_request = st.session_state.get(
        "rp2040_write_request"
    )

    result: RP2040DeviceResult = render_rp2040_device(
        baud_rate=115_200,
        write_request=write_request,
        key="rp2040_device",
    )

    if result.state.sid_exists:
        gateway_id, serial_ids = (
            _render_rp2040_state(
                state=result.state
            )
        )

        if serial_ids:
            _render_create_new_config_section(
                serial_ids
            )

    if result.state.error:
        st.error(
            result.state.error
        )


def _render_rp2040_state(
        state: RP2040DeviceState,
) -> tuple[str | None, list[str]]:
    st.divider()

    st.subheader(
        "Gateway Configuration"
    )

    gateway_text = "N/A"
    gateway_id: str | None = None
    serial_ids: list[str] = []

    if state.sid_exists:
        gateway_id = (
            state.sid
            .replace('{"sid":', "")
            .replace("}", "")
            .replace('"', "")
            .strip()
        )

        if gateway_id.startswith("A"):
            gateway_text = gateway_id
            serial_ids = _build_sensor_ids(state)
        else:
            gateway_text = (
                f"Non-Gateway device connected: {gateway_id}"
            )

    col1, col2, _col3 = st.columns([1, 1, 2])
    show_border: bool = False

    with col1:

        with st.container(border=show_border):
            st.caption("Gateway ID")
            st.code(gateway_text,
                    language=None,
                    )

    with col2:
        with st.container(border=show_border):
            st.caption("Sensor IDs")

            """
            if serial_ids:
                for serial_id in serial_ids:
                    st.code(
                        serial_id.strip(),
                        language=None,
                    )
            else:
                st.write("None")
            """

            if serial_ids:
                for index, sensor_id in enumerate(
                        serial_ids
                ):
                    id_col, move_col = st.columns(
                        [10, 1],
                        vertical_alignment="center",
                    )

                    with id_col:
                        st.code(
                            sensor_id,
                            language=None,
                            # height=_height,
                        )

                    with move_col:
                        move_clicked = st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"move_sensor_{index}",
                            help=(
                                f"Include {sensor_id} in new configuration."
                            ),
                            type="tertiary",
                        )

                    if move_clicked:
                        new_sensor_ids = st.session_state[
                            NEW_SENSOR_IDS_KEY
                        ]

                        if sensor_id not in new_sensor_ids:
                            new_sensor_ids.append(
                                sensor_id
                            )

                        st.rerun()

            else:
                st.write(
                    "None"
                )

    # st.divider()

    return gateway_id, serial_ids


def _build_sensor_ids(state: RP2040DeviceState) -> list[str]:
    if not state.did_exists:
        return []

    serial_ids_str: str = (state.did
                           .replace('{"dvc":', "")
                           .replace("{", "")
                           .replace("}", "")
                           .replace("[", "")
                           .replace("]", "")
                           .replace('"', "")
                           .strip()
                           )
    serial_ids: list[str] = serial_ids_str.split(",")
    return serial_ids


def _render_create_new_config_section(
        serial_ids: list[str],
) -> None:
    st.divider()

    _height: int = 50

    st.subheader(
        "Create New Pairing Configuration"
    )

    col1, col2, _col3 = st.columns([1, 1, 2])

    with col1:

        st.caption(
            "Input New Sensor ID"
        )

        """
        user_input = st.chat_input(
            "Sensor ID...",
            key=SENSOR_ID_INPUT_KEY,
        )
        """

        with st.form(
                "add_sensor_form",
                clear_on_submit=True,
                border=False,
                height=_height,
        ):
            input_col, button_col = st.columns(
                [8, 1],
                vertical_alignment="bottom",
            )

            with input_col:
                sensor_id = st.text_input(
                    "Sensor ID",
                    placeholder="Sensor ID...",
                    label_visibility="collapsed",
                )

            with button_col:
                user_input = st.form_submit_button(
                    "",
                    icon=":material/add:",
                    help="Add Sensor ID",
                    use_container_width=True,
                    type="tertiary"
                )

            if user_input:
                sensor_id = sensor_id.strip()
                # sensor_id = user_input  #.strip()

                if not _validate_user_input(
                        sensor_id
                ):
                    st.error(
                        "Invalid Sensor ID"
                    )

                elif sensor_id in st.session_state[
                    NEW_SENSOR_IDS_KEY
                ]:
                    st.warning(
                        "Sensor ID already added."
                    )

                else:
                    st.session_state[
                        NEW_SENSOR_IDS_KEY
                    ].append(
                        sensor_id
                    )

    with col2:
        st.caption(
            "Sensor IDs"
        )

        sensor_ids = st.session_state[
            NEW_SENSOR_IDS_KEY
        ]

        if sensor_ids:
            for index, sensor_id in enumerate(
                    sensor_ids
            ):
                id_col, delete_col = st.columns(
                    [10, 1],
                    vertical_alignment="center",
                )

                with id_col:
                    st.code(
                        sensor_id,
                        language=None,
                        # height=_height,
                    )

                with delete_col:
                    delete_clicked = st.button(
                        "",
                        icon=":material/delete:",
                        key=(
                            f"delete_sensor_"
                            f"{index}"
                        ),
                        help=(
                            f"Remove {sensor_id}"
                        ),
                        type="tertiary"
                    )

                if delete_clicked:
                    sensor_ids.pop(index)
                    st.rerun()

        else:
            st.write(
                "None"
            )

    flash_col, _col2 = st.columns([2, 5])

    with flash_col:
        flash_clicked = st.button(
            "Flash Sensor IDs",
            icon=":material/usb:",
            key=(
                f"flash_sensors"
            ),
            help=(
                f"Flash selected sensors to Gateway."
            ),
            type="primary"
        )

    if flash_clicked:
        content: bytes = _create_did_dot_dat_file()

        request_id = uuid4().hex

        st.session_state["rp2040_write_request"] = RP2040WriteRequest(
            request_id=request_id,
            filename="did.dat",
            content=content,
        )

        st.rerun()


def _validate_user_input(
        user_input: str,
) -> bool:
    if len(user_input) != _SENSOR_ID_LENGTH:
        return False

    return _is_hex_value(
        user_input
    )


def _handle_add_new_sensor_id():
    # st.success(f"Processed: {st.session_state.my_text}")

    st.session_state.add_sensor_id = ""


def _is_hex_value(
        value: str,
) -> bool:
    try:
        int(
            value,
            16,
        )
        return True

    except (
            ValueError,
            TypeError,
    ):
        return False


def _initialize_session_state() -> None:
    if NEW_SENSOR_IDS_KEY not in st.session_state:
        st.session_state[
            NEW_SENSOR_IDS_KEY
        ] = []


def _create_did_dot_dat_file() -> bytes:
    sensor_ids = list(st.session_state[NEW_SENSOR_IDS_KEY])

    file_content: dict[str, list[str]] = {"dvc": sensor_ids}

    content_bytes: bytes = json.dumps(
        file_content, separators=(',', ': ')).encode('utf-8')

    return content_bytes
