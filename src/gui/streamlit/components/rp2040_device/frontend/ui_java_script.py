# src/gui/streamlit/components/rp2040_device/frontend/ui_java_script.py

JS = r"""
const CTRL_A = 0x01;
const CTRL_B = 0x02;
const CTRL_C = 0x03;
const CTRL_D = 0x04;


class MicroPythonRawReplClient {

    constructor({
        baudRate = 115200,
        timeoutMs = 5000,
        interruptAttempts = 30,
        interruptIntervalMs = 25,
    } = {}) {
        this.baudRate = baudRate;
        this.timeoutMs = timeoutMs;

        this.interruptAttempts =
            interruptAttempts;

        this.interruptIntervalMs =
            interruptIntervalMs;

        /*
         * Keep the selected port after an intentional
         * disconnect so Refresh/Flash can reopen it.
         */
        this.port = null;

        this.reader = null;
        this.writer = null;

        this.rawReplActive = false;

        this.encoder =
            new TextEncoder();

        this.decoder =
            new TextDecoder();
    }


    get connected() {
        return (
            this.port !== null
            && this.reader !== null
            && this.writer !== null
        );
    }


    get hasPort() {
        return (
            this.port !== null
        );
    }


    _ensureWebSerialSupported() {
        if (!("serial" in navigator)) {
            throw new Error(
                "Web Serial is not supported by this browser."
            );
        }
    }


    async selectAndConnect() {
        this._ensureWebSerialSupported();

        if (this.connected) {
            return;
        }

        /*
         * Explicit Connect allows the operator to
         * select a device.
         */
        this.port =
            await navigator.serial.requestPort();

        try {
            await this._openSelectedPort();

        } catch (error) {
            await this._cleanupOpenSession();

            throw error;
        }
    }


    async reconnect() {
        this._ensureWebSerialSupported();

        if (this.connected) {
            return;
        }

        /*
         * Prefer the port remembered by this
         * component instance.
         */
        if (this.port) {
            await this._openSelectedPort();

            return;
        }

        /*
         * If Streamlit recreated the component,
         * recover an already-authorized port.
         */
        const ports =
            await navigator.serial.getPorts();

        if (ports.length === 0) {
            throw new Error(
                "No previously authorized serial device "
                + "is available. Select Connect first."
            );
        }

        if (ports.length > 1) {
            throw new Error(
                "Multiple authorized serial devices were found. "
                + "Select Connect and choose the RP2040 device."
            );
        }

        this.port =
            ports[0];

        await this._openSelectedPort();
    }


    async _openSelectedPort() {
        if (!this.port) {
            throw new Error(
                "No serial port has been selected."
            );
        }

        if (
            this.reader
            || this.writer
        ) {
            await this._cleanupOpenSession();
        }

        await this.port.open({
            baudRate: this.baudRate,
        });

        if (!this.port.readable) {
            throw new Error(
                "The serial port does not provide "
                + "a readable stream."
            );
        }

        if (!this.port.writable) {
            throw new Error(
                "The serial port does not provide "
                + "a writable stream."
            );
        }

        this.reader =
            this.port.readable.getReader();

        this.writer =
            this.port.writable.getWriter();

        this.rawReplActive =
            false;
    }


    async disconnect() {
        /*
         * Try to leave raw REPL gracefully first.
         */
        if (
            this.rawReplActive
            && this.connected
        ) {
            try {
                await this.exitRawRepl();
            } catch {
                // Ignore REPL cleanup errors.
            }
        }

        await this._cleanupOpenSession();

        /*
         * Close the port, but retain this.port so it
         * can be reopened without another picker.
         */
        if (this.port) {
            try {
                await this.port.close();

            } catch {
                /*
                 * Device may already have reset or
                 * physically disconnected.
                 */
            }
        }
    }


    async _cleanupOpenSession() {
        this.rawReplActive =
            false;

        if (this.reader) {
            try {
                await this.reader.cancel();
            } catch {
                // Ignore cancellation errors.
            }

            try {
                this.reader.releaseLock();
            } catch {
                // Ignore release errors.
            }

            this.reader = null;
        }

        if (this.writer) {
            try {
                this.writer.releaseLock();
            } catch {
                // Ignore release errors.
            }

            this.writer = null;
        }
    }


    handlePhysicalDisconnect() {
        this.rawReplActive =
            false;

        if (this.reader) {
            try {
                this.reader.releaseLock();
            } catch {
                // Ignore.
            }
        }

        if (this.writer) {
            try {
                this.writer.releaseLock();
            } catch {
                // Ignore.
            }
        }

        this.reader = null;
        this.writer = null;
        this.port = null;
    }


    async writeBytes(bytes) {
        if (!this.writer) {
            throw new Error(
                "Serial device is not connected."
            );
        }

        await this.writer.write(
            bytes
        );
    }


    async writeText(text) {
        await this.writeBytes(
            this.encoder.encode(
                text
            )
        );
    }


    async readUntil(
        predicate,
        timeoutMs = this.timeoutMs,
    ) {
        if (!this.reader) {
            throw new Error(
                "Serial device is not connected."
            );
        }

        const deadline =
            Date.now() + timeoutMs;

        let result = "";

        while (
            Date.now() < deadline
        ) {
            const {
                value,
                done,
            } = await this.reader.read();

            if (done) {
                throw new Error(
                    "Serial connection closed."
                );
            }

            if (value) {
                result +=
                    this.decoder.decode(
                        value,
                        {
                            stream: true,
                        }
                    );
            }

            if (
                predicate(result)
            ) {
                return result;
            }
        }

        throw new Error(
            "Timed out waiting for RP2040."
        );
    }


    async interruptRunningProgram() {
        const interrupt =
            new Uint8Array([
                CTRL_C,
            ]);

        /*
         * Approximately 750 ms of repeated Ctrl-C.
         */
        for (
            let attempt = 0;
            attempt < this.interruptAttempts;
            attempt++
        ) {
            await this.writeBytes(
                interrupt
            );

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        this.interruptIntervalMs
                    )
            );
        }
    }


    async enterRawRepl() {
        if (!this.connected) {
            throw new Error(
                "Serial device is not connected."
            );
        }

        if (this.rawReplActive) {
            return;
        }

        await this.interruptRunningProgram();

        /*
         * Give the interpreter a brief settling period.
         */
        await new Promise(
            resolve =>
                setTimeout(
                    resolve,
                    100
                )
        );

        await this.writeBytes(
            new Uint8Array([
                CTRL_A,
            ])
        );

        await this.readUntil(
            text =>
                text.includes(
                    "raw REPL"
                )
        );

        this.rawReplActive =
            true;
    }


    async exitRawRepl() {
        if (
            !this.connected
            || !this.rawReplActive
        ) {
            return;
        }

        await this.writeBytes(
            new Uint8Array([
                CTRL_B,
            ])
        );

        this.rawReplActive =
            false;
    }


    /*
     * Execute one command while raw REPL is ALREADY
     * active.
     *
     * This deliberately does not enter or exit raw
     * REPL.
     */
    async executeRaw(code) {
        if (!this.connected) {
            throw new Error(
                "Serial device is not connected."
            );
        }

        if (!this.rawReplActive) {
            throw new Error(
                "Raw REPL session is not active."
            );
        }

        await this.writeText(
            code
        );

        await this.writeBytes(
            new Uint8Array([
                CTRL_D,
            ])
        );

        const response =
            await this.readUntil(
                text =>
                    text.includes(
                        "\x04>"
                    )
            );

        return this.parseRawReplResponse(
            response
        );
    }


    /*
     * Enter raw REPL once, perform an arbitrary set
     * of operations, then exit once.
     */
    async runRawSession(operation) {
        if (!this.connected) {
            throw new Error(
                "Serial device is not connected."
            );
        }

        await this.enterRawRepl();

        try {
            return await operation();

        } finally {
            if (
                this.connected
                && this.rawReplActive
            ) {
                try {
                    await this.exitRawRepl();
                } catch {
                    /*
                     * Do not hide the original operation
                     * result/error because cleanup failed.
                     */
                    this.rawReplActive =
                        false;
                }
            }
        }
    }


    parseRawReplResponse(response) {
        let text =
            response;

        text =
            text.replace(
                /^raw REPL.*?>/s,
                ""
            );

        text =
            text.replace(
                /^OK/,
                ""
            );

        const parts =
            text.split(
                "\x04"
            );

        return {
            stdout:
                parts[0]
                ?? "",

            stderr:
                parts[1]
                ?? "",
        };
    }
}


class RP2040WebSerialFileService {

    constructor(options = {}) {
        this.client =
            new MicroPythonRawReplClient(
                options
            );
    }


    get connected() {
        return (
            this.client.connected
        );
    }


    get hasPort() {
        return (
            this.client.hasPort
        );
    }


    async selectAndConnect() {
        await this.client.selectAndConnect();
    }


    async reconnect() {
        await this.client.reconnect();
    }


    async disconnect() {
        await this.client.disconnect();
    }


    handlePhysicalDisconnect() {
        this.client.handlePhysicalDisconnect();
    }


    normalizeRemotePath(path) {
        if (!path) {
            return "/";
        }

        let normalized =
            path.replaceAll(
                "\\",
                "/"
            );

        normalized =
            "/"
            + normalized
                .split("/")
                .filter(Boolean)
                .join("/");

        return (
            normalized
            || "/"
        );
    }


    joinRemotePath(
        directory,
        name,
    ) {
        const parent =
            this.normalizeRemotePath(
                directory
            );

        if (parent === "/") {
            return `/${name}`;
        }

        return `${parent}/${name}`;
    }


    bytesToBase64(bytes) {
        let binary = "";

        for (
            let index = 0;
            index < bytes.length;
            index++
        ) {
            binary +=
                String.fromCharCode(
                    bytes[index]
                );
        }

        return btoa(
            binary
        );
    }


    base64ToBytes(base64) {
        const binary =
            atob(
                base64
            );

        const bytes =
            new Uint8Array(
                binary.length
            );

        for (
            let index = 0;
            index < binary.length;
            index++
        ) {
            bytes[index] =
                binary.charCodeAt(
                    index
                );
        }

        return bytes;
    }


    /*
     * --------------------------------------------------
     * Raw-session filesystem primitives
     * --------------------------------------------------
     *
     * These methods assume that raw REPL is already
     * active.
     */


    async fileExistsRaw(
        remotePath
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.client.executeRaw(`
import os

_path = ${JSON.stringify(path)}

try:
    os.stat(_path)
    print("1")
except OSError:
    print("0")
`);

        if (
            result.stderr.trim()
        ) {
            throw new Error(
                result.stderr.trim()
            );
        }

        return (
            result.stdout.trim()
            === "1"
        );
    }


    async readTextFileRaw(
        remotePath
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.client.executeRaw(`
_path = ${JSON.stringify(path)}

with open(_path, "r") as _file:
    print(_file.read().strip())
`);

        if (
            result.stderr.trim()
        ) {
            throw new Error(
                result.stderr.trim()
            );
        }

        return (
            result.stdout.trim()
        );
    }


    async writeFileRaw(
        remotePath,
        bytes,
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        /*
         * Create/truncate the file while remaining
         * inside the same raw REPL session.
         */
        const createResult =
            await this.client.executeRaw(`
with open(
    ${JSON.stringify(path)},
    "wb"
) as _file:
    pass
`);

        if (
            createResult.stderr.trim()
        ) {
            throw new Error(
                createResult.stderr.trim()
            );
        }

        const chunkSize =
            512;

        for (
            let offset = 0;
            offset < bytes.length;
            offset += chunkSize
        ) {
            const chunk =
                bytes.slice(
                    offset,
                    offset + chunkSize
                );

            const encoded =
                this.bytesToBase64(
                    chunk
                );

            const result =
                await this.client.executeRaw(`
import binascii

_data = binascii.a2b_base64(
    ${JSON.stringify(encoded)}
)

with open(
    ${JSON.stringify(path)},
    "ab"
) as _file:
    _file.write(_data)
`);

            if (
                result.stderr.trim()
            ) {
                throw new Error(
                    result.stderr.trim()
                );
            }
        }
    }


    async readDeviceMetadataRaw() {
        const sidExists =
            await this.fileExistsRaw(
                "/sid.dat"
            );

        const didExists =
            await this.fileExistsRaw(
                "/did.dat"
            );

        const sid =
            sidExists
                ? await this.readTextFileRaw(
                    "/sid.dat"
                )
                : null;

        const did =
            didExists
                ? await this.readTextFileRaw(
                    "/did.dat"
                )
                : null;

        return {
            sidExists,
            didExists,
            sid,
            did,
        };
    }


    /*
     * --------------------------------------------------
     * High-level READ transaction
     * --------------------------------------------------
     *
     * One interruption.
     * One raw REPL entry.
     * All metadata operations.
     * One raw REPL exit.
     */

    async readDeviceMetadata() {
        return await this.client.runRawSession(
            async () => {
                return await this.readDeviceMetadataRaw();
            }
        );
    }


    /*
     * --------------------------------------------------
     * High-level FLASH transaction
     * --------------------------------------------------
     *
     * One interruption.
     * One raw REPL entry.
     *
     * Within that single session:
     *   1. write file
     *   2. verify exact contents
     *   3. refresh SID/DID metadata
     *
     * Then exit raw REPL once.
     */

    async flashConfiguration(
        remotePath,
        contentBase64,
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const bytes =
            this.base64ToBytes(
                contentBase64
            );

        const expectedText =
            new TextDecoder()
                .decode(
                    bytes
                )
                .trim();

        return await this.client.runRawSession(
            async () => {

                await this.writeFileRaw(
                    path,
                    bytes
                );

                const actualText =
                    await this.readTextFileRaw(
                        path
                    );

                if (
                    actualText
                    !== expectedText
                ) {
                    throw new Error(
                        `${path} verification failed.`
                    );
                }

                const metadata =
                    await this.readDeviceMetadataRaw();

                return {
                    size:
                        bytes.length,

                    metadata:
                        metadata,
                };
            }
        );
    }
}


export default function(component) {

    const {
        parentElement,
        data,
        setStateValue,
        setTriggerValue,
    } = component;


    /*
     * --------------------------------------------------
     * DOM
     * --------------------------------------------------
     */

    const connectButton =
        parentElement.querySelector(
            "#connect-button"
        );

    const disconnectButton =
        parentElement.querySelector(
            "#disconnect-button"
        );

    const refreshButton =
        parentElement.querySelector(
            "#refresh-button"
        );

    const deviceStatus =
        parentElement.querySelector(
            "#device-status"
        );


    if (
        !connectButton
        || !disconnectButton
        || !refreshButton
        || !deviceStatus
    ) {
        throw new Error(
            "RP2040 component HTML is missing "
            + "one or more required elements."
        );
    }


    /*
     * --------------------------------------------------
     * Persistent service
     * --------------------------------------------------
     */

    if (
        !parentElement.__rp2040Service
    ) {
        parentElement.__rp2040Service =
            new RP2040WebSerialFileService({
                baudRate:
                    data?.baudRate
                    ?? 115200,

                timeoutMs:
                    data?.timeoutMs
                    ?? 5000,

                interruptAttempts:
                    data?.interruptAttempts
                    ?? 30,

                interruptIntervalMs:
                    data?.interruptIntervalMs
                    ?? 25,
            });
    }

    const service =
        parentElement.__rp2040Service;


    /*
     * --------------------------------------------------
     * UI / component-state helpers
     * --------------------------------------------------
     */

    function setStatus(message) {
        setStateValue(
            "status",
            message
        );
    }


    function setError(message) {
        setStateValue(
            "error",
            message
        );
    }


    function clearError() {
        setStateValue(
            "error",
            null
        );
    }


    function clearMetadata() {
        setStateValue(
            "sid_exists",
            false
        );

        setStateValue(
            "did_exists",
            false
        );

        setStateValue(
            "sid",
            null
        );

        setStateValue(
            "did",
            null
        );
    }


    function applyMetadata(
        metadata
    ) {
        setStateValue(
            "sid_exists",
            metadata.sidExists
        );

        setStateValue(
            "did_exists",
            metadata.didExists
        );

        setStateValue(
            "sid",
            metadata.sid
        );

        setStateValue(
            "did",
            metadata.did
        );
    }


    function setConnectionUi(
        connected
    ) {
        setStateValue(
            "connected",
            connected
        );

        deviceStatus.innerHTML =
            connected
                ? (
                    "Connection Status: "
                    + "<strong>Connected</strong>"
                )
                : (
                    "Connection Status: "
                    + "<strong>Not Connected</strong>"
                );

        connectButton.disabled =
            connected;

        disconnectButton.disabled =
            !connected;

        /*
         * Refresh can reopen a remembered port after
         * an intentional disconnect.
         */
        refreshButton.disabled =
            (
                connected
                || !service.hasPort
            );
    }


    /*
     * --------------------------------------------------
     * Maintenance-session cleanup
     * --------------------------------------------------
     */

    async function closeMaintenanceSession() {
        try {
            if (service.connected) {
                await service.disconnect();
            }

        } finally {
            setConnectionUi(
                false
            );
        }
    }


    /*
     * --------------------------------------------------
     * Read configuration snapshot
     * --------------------------------------------------
     */

    async function acquireDeviceMetadata() {
        clearError();

        setStatus(
            "Reading device configuration..."
        );

        const metadata =
            await service.readDeviceMetadata();

        applyMetadata(
            metadata
        );

        return metadata;
    }


    /*
     * --------------------------------------------------
     * Explicit Connect
     * --------------------------------------------------
     */

    connectButton.onclick =
        async () => {

            clearError();

            /*
             * The user is explicitly selecting a new
             * device, so discard the old snapshot.
             */
            clearMetadata();

            try {
                setStatus(
                    "Selecting device..."
                );

                await service.selectAndConnect();

                setConnectionUi(
                    true
                );

                await acquireDeviceMetadata();

                await closeMaintenanceSession();

                setStatus(
                    "Configuration loaded."
                );

            } catch (error) {
                try {
                    await closeMaintenanceSession();
                } catch {
                    // Ignore cleanup errors.
                }

                setError(
                    "Unable to read device configuration: "
                    + error.message
                );
            }
        };


    /*
     * --------------------------------------------------
     * Refresh existing device
     * --------------------------------------------------
     */

    refreshButton.onclick =
        async () => {

            clearError();

            /*
             * Keep the previous snapshot visible until
             * a replacement snapshot is successfully
             * acquired.
             */
            try {
                setStatus(
                    "Reconnecting..."
                );

                await service.reconnect();

                setConnectionUi(
                    true
                );

                await acquireDeviceMetadata();

                await closeMaintenanceSession();

                setStatus(
                    "Configuration refreshed."
                );

            } catch (error) {
                try {
                    await closeMaintenanceSession();
                } catch {
                    // Ignore cleanup errors.
                }

                setError(
                    "Unable to refresh device configuration: "
                    + error.message
                );
            }
        };


    /*
     * --------------------------------------------------
     * Explicit Disconnect
     * --------------------------------------------------
     */

    disconnectButton.onclick =
        async () => {

            try {
                await closeMaintenanceSession();

                /*
                 * SID/DID snapshot is intentionally
                 * preserved.
                 */
                setStatus(
                    "Disconnected. "
                    + "Showing last-read configuration."
                );

            } catch (error) {
                setError(
                    "Disconnect failed: "
                    + error.message
                );
            }
        };


    /*
     * --------------------------------------------------
     * Write-request helpers
     * --------------------------------------------------
     */

    function validateWriteRequest(
        request
    ) {
        if (!request) {
            return false;
        }

        if (!request.filename) {
            throw new Error(
                "Write request does not contain a filename."
            );
        }

        if (!request.contentBase64) {
            throw new Error(
                "Write request does not contain file contents."
            );
        }

        return true;
    }


    function getWriteRequestKey(
        request
    ) {
        return (
            request.requestId
            ?? (
                request.filename
                + ":"
                + request.contentBase64
            )
        );
    }


    /*
     * --------------------------------------------------
     * Python -> JavaScript Flash request
     * --------------------------------------------------
     */

    async function processWriteRequest() {
        const request =
            data?.writeRequest;

        if (
            !validateWriteRequest(
                request
            )
        ) {
            return;
        }

        const requestKey =
            getWriteRequestKey(
                request
            );


        /*
         * Ignore an already-completed request.
         */
        if (
            parentElement.__lastRp2040WriteRequest
            === requestKey
        ) {
            return;
        }


        /*
         * Prevent concurrent writes caused by multiple
         * component executions.
         */
        if (
            parentElement.__rp2040WriteInProgress
        ) {
            return;
        }

        parentElement.__rp2040WriteInProgress =
            true;


        try {
            clearError();

            setStatus(
                "Reconnecting to device..."
            );

            await service.reconnect();

            setConnectionUi(
                true
            );


            const remotePath =
                service.joinRemotePath(
                    "/",
                    request.filename
                );


            setStatus(
                `Writing ${request.filename}...`
            );


            /*
             * IMPORTANT:
             *
             * flashConfiguration() performs the entire
             * operation in ONE raw REPL session:
             *
             * write
             * verify
             * refresh metadata
             */

            const result =
                await service.flashConfiguration(
                    remotePath,
                    request.contentBase64
                );


            applyMetadata(
                result.metadata
            );


            /*
             * Only mark the request complete after the
             * write and verification both succeeded.
             */

            parentElement.__lastRp2040WriteRequest =
                requestKey;


            /*
             * Release the serial port before notifying
             * Python.
             */

            await closeMaintenanceSession();


            setStatus(
                `${request.filename} flashed successfully.`
            );


            setTriggerValue(
                "transfer_complete",
                {
                    requestId:
                        request.requestId
                        ?? null,

                    filename:
                        request.filename,

                    destination:
                        remotePath,

                    size:
                        result.size,
                }
            );


        } catch (error) {
            try {
                await closeMaintenanceSession();
            } catch {
                // Ignore cleanup errors.
            }

            setError(
                "Write failed: "
                + error.message
            );

        } finally {
            parentElement.__rp2040WriteInProgress =
                false;
        }
    }


    /*
     * --------------------------------------------------
     * Physical USB disconnect
     * --------------------------------------------------
     */

    function handleDisconnect(event) {
        const currentPort =
            service.client.port;

        /*
         * Ignore disconnects belonging to some other
         * serial device.
         */
        if (
            currentPort
            && event.target !== currentPort
        ) {
            return;
        }

        service.handlePhysicalDisconnect();

        /*
         * Preserve the last successfully acquired
         * configuration snapshot.
         */
        setConnectionUi(
            false
        );

        setStatus(
            "Device disconnected. "
            + "Showing last-read configuration."
        );
    }


    navigator.serial?.addEventListener(
        "disconnect",
        handleDisconnect
    );


    /*
     * --------------------------------------------------
     * Initial UI synchronization
     * --------------------------------------------------
     */

    setConnectionUi(
        service.connected
    );


    /*
     * --------------------------------------------------
     * Incoming Flash request
     * --------------------------------------------------
     */

    if (
        data?.writeRequest
    ) {
        void processWriteRequest();
    }


    /*
     * --------------------------------------------------
     * Cleanup
     * --------------------------------------------------
     *
     * Do not disconnect here. Streamlit may execute
     * this cleanup because the component was rerendered,
     * not because the user intended to close the device.
     */

    return () => {
        navigator.serial?.removeEventListener(
            "disconnect",
            handleDisconnect
        );
    };
}
"""
