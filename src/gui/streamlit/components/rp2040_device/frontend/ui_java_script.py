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
    } = {}) {
        this.baudRate = baudRate;
        this.timeoutMs = timeoutMs;

        this.port = null;
        this.reader = null;
        this.writer = null;

        this.encoder = new TextEncoder();
        this.decoder = new TextDecoder();
    }


    get connected() {
        return this.port !== null;
    }


    async connect() {
        if (!("serial" in navigator)) {
            throw new Error(
                "Web Serial is not supported by this browser."
            );
        }

        if (this.connected) {
            return;
        }

        try {
            this.port =
                await navigator.serial.requestPort();

            await this.port.open({
                baudRate: this.baudRate,
            });

            this.reader =
                this.port.readable.getReader();

            this.writer =
                this.port.writable.getWriter();

        } catch (error) {
            this.handlePhysicalDisconnect();
            throw error;
        }
    }


    async disconnect() {
        if (this.reader) {
            try {
                await this.reader.cancel();
            } catch {
                // Ignore cancellation errors.
            }

            try {
                this.reader.releaseLock();
            } catch {
                // Ignore lock release errors.
            }

            this.reader = null;
        }

        if (this.writer) {
            try {
                this.writer.releaseLock();
            } catch {
                // Ignore lock release errors.
            }

            this.writer = null;
        }

        if (this.port) {
            const port = this.port;

            this.port = null;

            try {
                await port.close();
            } catch {
                // Device may already have been removed.
            }
        }
    }


    handlePhysicalDisconnect() {
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

        await this.writer.write(bytes);
    }


    async writeText(text) {
        await this.writeBytes(
            this.encoder.encode(text)
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

        while (Date.now() < deadline) {
            const { value, done } =
                await this.reader.read();

            if (done) {
                throw new Error(
                    "Serial connection closed."
                );
            }

            if (value) {
                result +=
                    this.decoder.decode(
                        value,
                        { stream: true },
                    );
            }

            if (predicate(result)) {
                return result;
            }
        }

        throw new Error(
            "Timed out waiting for RP2040."
        );
    }


    async enterRawRepl() {
        await this.writeBytes(
            new Uint8Array([
                CTRL_C,
                CTRL_C,
            ])
        );

        await new Promise(
            resolve =>
                setTimeout(resolve, 100)
        );

        await this.writeBytes(
            new Uint8Array([
                CTRL_A,
            ])
        );

        await this.readUntil(
            text =>
                text.includes("raw REPL")
        );
    }


    async exitRawRepl() {
        await this.writeBytes(
            new Uint8Array([
                CTRL_B,
            ])
        );
    }


    async execute(code) {
        if (!this.connected) {
            throw new Error(
                "RP2040 is not connected."
            );
        }

        await this.enterRawRepl();

        try {
            await this.writeText(code);

            await this.writeBytes(
                new Uint8Array([
                    CTRL_D,
                ])
            );

            const response =
                await this.readUntil(
                    text =>
                        text.includes("\x04>")
                );

            return this.parseRawReplResponse(
                response
            );

        } finally {
            await this.exitRawRepl();
        }
    }


    parseRawReplResponse(response) {
        let text = response;

        text = text.replace(
            /^raw REPL.*?>/s,
            ""
        );

        text = text.replace(
            /^OK/,
            ""
        );

        const parts =
            text.split("\x04");

        return {
            stdout:
                parts[0] ?? "",

            stderr:
                parts[1] ?? "",
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
        return this.client.connected;
    }


    async connect() {
        await this.client.connect();
    }


    async disconnect() {
        await this.client.disconnect();
    }


    handlePhysicalDisconnect() {
        this.client.handlePhysicalDisconnect();
    }


    async execute(code) {
        return await this.client.execute(
            code
        );
    }


    normalizeRemotePath(path) {
        if (!path) {
            return "/";
        }

        let normalized =
            path.replaceAll("\\", "/");

        normalized =
            "/" +
            normalized
                .split("/")
                .filter(Boolean)
                .join("/");

        return normalized || "/";
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

        return btoa(binary);
    }


    base64ToBytes(base64) {
        const binary =
            atob(base64);

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
                binary.charCodeAt(index);
        }

        return bytes;
    }


    async writeFile(
        remotePath,
        bytes,
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        /*
         * Create or truncate the destination file.
         */
        const createResult =
            await this.execute(`
with open(
    ${JSON.stringify(path)},
    "wb"
) as _file:
    pass
`);

        if (createResult.stderr.trim()) {
            throw new Error(
                createResult.stderr.trim()
            );
        }

        /*
         * Transfer in small chunks so that the
         * MicroPython REPL command remains small.
         */
        const chunkSize = 512;

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
                await this.execute(`
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

            if (result.stderr.trim()) {
                throw new Error(
                    result.stderr.trim()
                );
            }
        }
    }


    async writeBase64File(
        remotePath,
        contentBase64,
    ) {
        const bytes =
            this.base64ToBytes(
                contentBase64
            );

        await this.writeFile(
            remotePath,
            bytes
        );

        return bytes.length;
    }


    async fileExists(remotePath) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.execute(`
import os

_path = ${JSON.stringify(path)}

try:
    os.stat(_path)
    print("1")
except OSError:
    print("0")
`);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr.trim()
            );
        }

        return result.stdout.trim() === "1";
    }


    async readTextFile(remotePath) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.execute(`
_path = ${JSON.stringify(path)}

with open(_path, "r") as _file:
    print(_file.read().strip())
`);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr.trim()
            );
        }

        return result.stdout.trim();
    }


    async readDeviceMetadata() {
        const sidExists =
            await this.fileExists(
                "/sid.dat"
            );

        const didExists =
            await this.fileExists(
                "/did.dat"
            );

        const sid =
            sidExists
                ? await this.readTextFile(
                    "/sid.dat"
                )
                : null;

        const did =
            didExists
                ? await this.readTextFile(
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


    /*
     * --------------------------------------------------
     * Validate component HTML
     * --------------------------------------------------
     */

    if (
        !connectButton
        || !disconnectButton
        || !refreshButton
        || !deviceStatus
    ) {
        throw new Error(
            "RP2040 component HTML is missing one or more required elements."
        );
    }


    /*
     * --------------------------------------------------
     * Persistent browser-side service
     * --------------------------------------------------
     *
     * Reuse the same service object when Streamlit
     * updates the component so that we do not
     * intentionally create another serial session.
     */

    if (!parentElement.__rp2040Service) {
        parentElement.__rp2040Service =
            new RP2040WebSerialFileService({
                baudRate:
                    data?.baudRate
                    ?? 115200,

                timeoutMs:
                    data?.timeoutMs
                    ?? 5000,
            });
    }

    const service =
        parentElement.__rp2040Service;


    /*
     * --------------------------------------------------
     * Helpers
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


    function setConnectionUi(
        connected
    ) {
        setStateValue(
            "connected",
            connected
        );

        deviceStatus.innerHTML =
            connected
                ? "Connection Status: <strong>Connected</strong>"
                : "Connection Status: <strong>Not Connected</strong>";

        connectButton.disabled =
            connected;

        disconnectButton.disabled =
            !connected;

        refreshButton.disabled =
            !connected;
    }


    async function refreshMetadata() {
        clearError();

        setStatus(
            "Reading device metadata..."
        );

        const metadata =
            await service.readDeviceMetadata();

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

        setStatus(
            "Device ready."
        );

        return metadata;
    }


    /*
     * --------------------------------------------------
     * Process Python -> JavaScript write request
     * --------------------------------------------------
     */

    async function processWriteRequest() {
        const request =
            data?.writeRequest;

        if (!request) {
            return;
        }

        if (!service.connected) {
            return;
        }

        if (
            !request.filename
            || !request.contentBase64
        ) {
            setError(
                "Invalid RP2040 write request."
            );

            return;
        }

        /*
         * Prefer an explicit requestId supplied by
         * Python. The fallback signature still prevents
         * accidental duplicate execution during a
         * component update.
         */
        const requestKey =
            request.requestId
            ?? (
                request.filename
                + ":"
                + request.contentBase64
            );

        if (
            parentElement.__lastRp2040WriteRequest
            === requestKey
        ) {
            return;
        }

        try {
            clearError();

            const remotePath =
                service.joinRemotePath(
                    "/",
                    request.filename
                );

            setStatus(
                `Writing ${request.filename}...`
            );

            const size =
                await service.writeBase64File(
                    remotePath,
                    request.contentBase64
                );

            /*
             * Mark the request completed only after
             * the write succeeds.
             */
            parentElement.__lastRp2040WriteRequest =
                requestKey;

            /*
             * Re-read sid.dat/did.dat after writing.
             * This also acts as a practical verification
             * that did.dat can be read back.
             */
            await refreshMetadata();

            setStatus(
                `${request.filename} written successfully.`
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
                        size,
                }
            );

        } catch (error) {
            setError(
                `Write failed: ${error.message}`
            );
        }
    }


    /*
     * --------------------------------------------------
     * Connect
     * --------------------------------------------------
     */

    connectButton.onclick =
        async () => {

            clearError();

            try {
                setStatus(
                    "Connecting..."
                );

                await service.connect();

            } catch (error) {
                setConnectionUi(
                    false
                );

                setError(
                    `Connection failed: ${error.message}`
                );

                return;
            }

            setConnectionUi(
                true
            );

            clearMetadata();

            try {
                await refreshMetadata();

                /*
                 * A write request may already have been
                 * supplied before the user connected.
                 */
                await processWriteRequest();

            } catch (error) {
                setError(
                    `Unable to initialize device: ${error.message}`
                );
            }
        };


    /*
     * --------------------------------------------------
     * Refresh metadata
     * --------------------------------------------------
     */

    refreshButton.onclick =
        async () => {

            if (!service.connected) {
                return;
            }

            try {
                await refreshMetadata();

            } catch (error) {
                setError(
                    `Unable to read device metadata: ${error.message}`
                );
            }
        };


    /*
     * --------------------------------------------------
     * Disconnect
     * --------------------------------------------------
     */

    disconnectButton.onclick =
        async () => {

            try {
                await service.disconnect();

                clearMetadata();

                setConnectionUi(
                    false
                );

                setStatus(
                    "Disconnected"
                );

            } catch (error) {
                setError(
                    `Disconnect failed: ${error.message}`
                );
            }
        };


    /*
     * --------------------------------------------------
     * Physical USB disconnect
     * --------------------------------------------------
     */

    function handleDisconnect(event) {
        const currentPort =
            service.client.port;

        if (
            currentPort
            && event.target !== currentPort
        ) {
            return;
        }

        service.handlePhysicalDisconnect();

        clearMetadata();

        setConnectionUi(
            false
        );

        setStatus(
            "Serial device disconnected."
        );
    }


    navigator.serial?.addEventListener(
        "disconnect",
        handleDisconnect
    );


    /*
     * --------------------------------------------------
     * Synchronize component with existing JS session
     * --------------------------------------------------
     */

    setConnectionUi(
        service.connected
    );


    /*
     * A new write request can arrive on a Streamlit
     * rerun while the browser-side serial service is
     * still connected.
     */

    if (
        service.connected
        && data?.writeRequest
    ) {
        void processWriteRequest();
    }


    /*
     * --------------------------------------------------
     * Cleanup
     * --------------------------------------------------
     *
     * Do not disconnect the serial service here.
     * Streamlit can rerender/update the component and
     * we want to preserve the browser-side connection.
     */

    return () => {
        navigator.serial?.removeEventListener(
            "disconnect",
            handleDisconnect
        );
    };
}
"""
