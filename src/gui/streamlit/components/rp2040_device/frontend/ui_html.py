# src/gui/streamlit/components/rp2040_device/frontend/ui_html.py

HTML = """
<div class="rp2040-device">

    <div class="field">
        <label>RP2040 Device</label>

        <div class="button-row">
            <button id="connect-button">
                Connect Device
            </button>

            <button id="disconnect-button" disabled>
                Disconnect
            </button>

            <button id="refresh-button" disabled>
                Refresh
            </button>
        </div>

        <div id="device-status">
            Not connected
        </div>
    </div>


    <div class="field">
        <label>Device Files</label>

        <div id="current-directory">
            /
        </div>

        <div id="file-list">
            Connect a device to view files.
        </div>
    </div>


    <hr />


    <div class="field">
        <label>Local File</label>

        <input
            id="file-input"
            type="file"
        />

        <div id="selected-file">
            No file selected
        </div>
    </div>


    <div class="field">
        <label>Destination</label>

        <input
            id="destination-input"
            type="text"
            value="/"
        />
    </div>


    <div class="field">
        <button
            id="upload-button"
            class="primary"
            disabled
        >
            Upload File
        </button>
    </div>


    <div class="field">
        <progress
            id="progress"
            value="0"
            max="100"
        ></progress>

        <div id="progress-text">
            0%
        </div>
    </div>


    <div id="status">
        Ready
    </div>

</div>
"""


