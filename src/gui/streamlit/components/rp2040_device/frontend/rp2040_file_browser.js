// src/gui/streamlit/components/rp2040_device/frontend/rp2040_file_browser.js

import {
    RP2040WebSerialFileService
} from "./rp2040_web_serial_service.js";


export default function(component) {

    const {
        parentElement,
        setStateValue,
        setTriggerValue,
    } = component;


    const service =
        new RP2040WebSerialFileService({
            baudRate: 115200,
        });


    const connectButton =
        parentElement.querySelector(
            "#connect-button"
        );

    const refreshButton =
        parentElement.querySelector(
            "#refresh-button"
        );


    async function refreshDirectory() {
        const entries =
            await service.listDirectory(
                "/"
            );

        setStateValue(
            "entries",
            entries
        );
    }


    connectButton.onclick =
        async () => {

            try {
                setStateValue(
                    "error",
                    null
                );

                await service.connect();

                setStateValue(
                    "connected",
                    true
                );

                await refreshDirectory();

            } catch (error) {
                setStateValue(
                    "error",
                    error.message
                );
            }
        };


    refreshButton.onclick =
        async () => {

            try {
                setStateValue(
                    "error",
                    null
                );

                await refreshDirectory();

            } catch (error) {
                setStateValue(
                    "error",
                    error.message
                );
            }
        };
}
