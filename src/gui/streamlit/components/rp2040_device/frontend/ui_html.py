# src/gui/streamlit/components/rp2040_device/frontend/ui_html.py

HTML = """
<div class="rp2040-device">

    <div class="field">

        <div class="button-row">

            <button
                id="connect-button"
                class="st-primary-button"
            >
                Connect
            </button>

            <button
                id="connect-button"
                class="st-primary-button"
            >
                Connect
            </button>
            
            <button
                id="disconnect-button"
                class="st-secondary-button"
                disabled
            >
                Disconnect
            </button>
            
            <button
                id="refresh-button"
                class="st-secondary-button"
                disabled
            >
                Refresh
            </button>

        </div>

        <div id="device-status">
            Connection Status:
            <strong>Not Connected</strong>
        </div>

    </div>

</div>
"""


