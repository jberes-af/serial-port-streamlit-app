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

        this.port =
            await navigator.serial.requestPort();

        await this.port.open({
            baudRate: this.baudRate,
        });

        this.reader =
            this.port.readable.getReader();

        this.writer =
            this.port.writable.getWriter();
    }


    async disconnect() {
        if (this.reader) {
            try {
                await this.reader.cancel();
            } catch {
                // Ignore cancellation errors.
            }

            this.reader.releaseLock();
            this.reader = null;
        }

        if (this.writer) {
            this.writer.releaseLock();
            this.writer = null;
        }

        if (this.port) {
            await this.port.close();
            this.port = null;
        }
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


    parentRemotePath(path) {
        const normalized =
            this.normalizeRemotePath(
                path
            );

        const parts =
            normalized
                .split("/")
                .filter(Boolean);

        parts.pop();

        if (parts.length === 0) {
            return "/";
        }

        return "/" + parts.join("/");
    }


    async listDirectory(
        remoteDirectory = "/",
    ) {
        const path =
            this.normalizeRemotePath(
                remoteDirectory
            );

        const code = `
import os

_path = ${JSON.stringify(path)}

for _entry in os.ilistdir(_path):
    _name = _entry[0]
    _type = _entry[1]
    _is_dir = (_type == 0x4000)

    if _is_dir:
        print("D|" + _name + "|")
    else:
        try:
            _size = _entry[3]
        except:
            _size = -1

        print(
            "F|" +
            _name +
            "|" +
            str(_size)
        )
`;

        const result =
            await this.execute(code);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr.trim()
            );
        }

        return this.parseDirectoryListing(
            result.stdout,
            path,
        );
    }


    parseDirectoryListing(
        output,
        remoteDirectory,
    ) {
        const entries = [];

        for (
            const rawLine
            of output.split(/\r?\n/)
        ) {
            const line =
                rawLine.trim();

            if (!line) {
                continue;
            }

            const [
                type,
                name,
                sizeText,
            ] = line.split("|");

            if (
                type !== "F"
                && type !== "D"
            ) {
                continue;
            }

            const isDirectory =
                type === "D";

            let size = null;

            if (!isDirectory) {
                const parsedSize =
                    Number(sizeText);

                size =
                    Number.isFinite(parsedSize)
                    && parsedSize >= 0
                        ? parsedSize
                        : null;
            }

            entries.push({
                name,

                path:
                    this.joinRemotePath(
                        remoteDirectory,
                        name,
                    ),

                isDirectory,
                size,
            });
        }

        entries.sort(
            (a, b) => {
                if (
                    a.isDirectory
                    !== b.isDirectory
                ) {
                    return (
                        a.isDirectory
                            ? -1
                            : 1
                    );
                }

                return a.name.localeCompare(
                    b.name
                );
            }
        );

        return entries;
    }


    bytesToBase64(bytes) {
        let binary = "";

        for (
            let i = 0;
            i < bytes.length;
            i++
        ) {
            binary +=
                String.fromCharCode(
                    bytes[i]
                );
        }

        return btoa(binary);
    }


    async writeFile(
        remotePath,
        bytes,
        onProgress = null,
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        /*
         * Create/truncate remote file.
         */
        const createResult =
            await this.execute(`
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

            if (onProgress) {
                const completed =
                    Math.min(
                        offset + chunk.length,
                        bytes.length
                    );

                onProgress(
                    completed / bytes.length
                );
            }
        }
    }


    async writeLocalFile(
        file,
        remoteDirectory = "/",
        onProgress = null,
    ) {
        const remotePath =
            this.joinRemotePath(
                remoteDirectory,
                file.name,
            );

        const buffer =
            await file.arrayBuffer();

        const bytes =
            new Uint8Array(
                buffer
            );

        await this.writeFile(
            remotePath,
            bytes,
            onProgress,
        );

        return remotePath;
    }


    async deleteFile(remotePath) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.execute(`
import os

os.remove(
    ${JSON.stringify(path)}
)
`);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr.trim()
            );
        }
    }


    async createDirectory(remotePath) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const result =
            await this.execute(`
import os

os.mkdir(
    ${JSON.stringify(path)}
)
`);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr.trim()
            );
        }
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

    const fileInput =
        parentElement.querySelector(
            "#file-input"
        );

    const selectedFileElement =
        parentElement.querySelector(
            "#selected-file"
        );

    const destinationInput =
        parentElement.querySelector(
            "#destination-input"
        );

    const uploadButton =
        parentElement.querySelector(
            "#upload-button"
        );

    const fileList =
        parentElement.querySelector(
            "#file-list"
        );

    const currentDirectoryElement =
        parentElement.querySelector(
            "#current-directory"
        );

    const deviceStatus =
        parentElement.querySelector(
            "#device-status"
        );

    const statusElement =
        parentElement.querySelector(
            "#status"
        );

    const progressElement =
        parentElement.querySelector(
            "#progress"
        );

    const progressText =
        parentElement.querySelector(
            "#progress-text"
        );


    /*
     * --------------------------------------------------
     * State
     * --------------------------------------------------
     */

    const service =
        new RP2040WebSerialFileService({
            baudRate:
                data?.baudRate
                ?? 115200,

            timeoutMs:
                data?.timeoutMs
                ?? 5000,
        });


    let selectedFile = null;

    let currentDirectory =
        data?.destination
        ?? "/";


    destinationInput.value =
        currentDirectory;


    /*
     * --------------------------------------------------
     * Helpers
     * --------------------------------------------------
     */

    function setStatus(message) {
        statusElement.textContent =
            message;

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

        statusElement.textContent =
            message;
    }


    function clearError() {
        setStateValue(
            "error",
            null
        );
    }


    function setProgress(fraction) {
        const value =
            Math.max(
                0,
                Math.min(
                    100,
                    fraction * 100
                )
            );

        progressElement.value =
            value;

        progressText.textContent =
            `${Math.round(value)}%`;
    }


    function refreshButtons() {
        const connected =
            service.connected;

        connectButton.disabled =
            connected;

        disconnectButton.disabled =
            !connected;

        refreshButton.disabled =
            !connected;

        uploadButton.disabled =
            !connected
            || !selectedFile;
    }


    function renderEntries(entries) {
        fileList.innerHTML = "";

        if (
            currentDirectory !== "/"
        ) {
            const parentEntry =
                document.createElement(
                    "div"
                );

            parentEntry.className =
                "file-entry directory-entry";

            parentEntry.textContent =
                "📁 ..";

            parentEntry.onclick =
                async () => {
                    currentDirectory =
                        service.parentRemotePath(
                            currentDirectory
                        );

                    await refreshDirectory();
                };

            fileList.appendChild(
                parentEntry
            );
        }

        if (entries.length === 0) {
            const empty =
                document.createElement(
                    "div"
                );

            empty.textContent =
                "Directory is empty.";

            fileList.appendChild(
                empty
            );

            return;
        }

        for (
            const entry
            of entries
        ) {
            const row =
                document.createElement(
                    "div"
                );

            row.className =
                entry.isDirectory
                    ? "file-entry directory-entry"
                    : "file-entry";

            if (entry.isDirectory) {
                row.textContent =
                    `📁 ${entry.name}`;

                row.onclick =
                    async () => {
                        currentDirectory =
                            entry.path;

                        await refreshDirectory();
                    };

            } else {
                const sizeText =
                    entry.size === null
                        ? ""
                        : ` (${entry.size} bytes)`;

                row.textContent =
                    `📄 ${entry.name}${sizeText}`;
            }

            fileList.appendChild(
                row
            );
        }
    }


    async function refreshDirectory() {
        clearError();

        setStatus(
            `Reading ${currentDirectory}...`
        );

        const entries =
            await service.listDirectory(
                currentDirectory
            );

        currentDirectoryElement.textContent =
            currentDirectory;

        destinationInput.value =
            currentDirectory;

        renderEntries(entries);

        setStateValue(
            "entries",
            entries
        );

        setStateValue(
            "current_directory",
            currentDirectory
        );

        setStatus("Ready");
    }


    /*
     * --------------------------------------------------
     * Connect
     * --------------------------------------------------
     */

    connectButton.onclick =
        async () => {

            try {
                clearError();

                setStatus(
                    "Connecting..."
                );

                await service.connect();

                setStateValue(
                    "connected",
                    true
                );

                deviceStatus.textContent =
                    "Connected";

                refreshButtons();

                await refreshDirectory();

            } catch (error) {
                setStateValue(
                    "connected",
                    false
                );

                deviceStatus.textContent =
                    "Not connected";

                setError(
                    error.message
                );

                refreshButtons();
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

                setStateValue(
                    "connected",
                    false
                );

                deviceStatus.textContent =
                    "Not connected";

                setStatus(
                    "Disconnected"
                );

            } catch (error) {
                setError(
                    error.message
                );

            } finally {
                refreshButtons();
            }
        };


    /*
     * --------------------------------------------------
     * Refresh
     * --------------------------------------------------
     */

    refreshButton.onclick =
        async () => {

            try {
                await refreshDirectory();

            } catch (error) {
                setError(
                    error.message
                );
            }
        };


    /*
     * --------------------------------------------------
     * Local file selection
     * --------------------------------------------------
     */

    fileInput.onchange =
        () => {

            selectedFile =
                fileInput.files?.[0]
                ?? null;

            if (!selectedFile) {
                selectedFileElement.textContent =
                    "No file selected";

                setStateValue(
                    "filename",
                    null
                );

                setStateValue(
                    "file_size",
                    null
                );

                refreshButtons();

                return;
            }

            selectedFileElement.textContent =
                `${selectedFile.name} `
                + `(${selectedFile.size} bytes)`;

            setStateValue(
                "filename",
                selectedFile.name
            );

            setStateValue(
                "file_size",
                selectedFile.size
            );

            refreshButtons();
        };


    /*
     * --------------------------------------------------
     * Upload
     * --------------------------------------------------
     */

    uploadButton.onclick =
        async () => {

            if (!selectedFile) {
                return;
            }

            try {
                clearError();

                uploadButton.disabled =
                    true;

                setProgress(0);

                setStatus(
                    `Uploading ${selectedFile.name}...`
                );

                const destination =
                    service.normalizeRemotePath(
                        destinationInput.value
                        || currentDirectory
                    );

                const remotePath =
                    await service.writeLocalFile(
                        selectedFile,
                        destination,
                        setProgress,
                    );

                setProgress(1);

                setStatus(
                    `Uploaded ${remotePath}`
                );

                setTriggerValue(
                    "transfer_complete",
                    {
                        filename:
                            selectedFile.name,

                        destination:
                            remotePath,

                        size:
                            selectedFile.size,
                    }
                );

                currentDirectory =
                    destination;

                await refreshDirectory();

            } catch (error) {
                setError(
                    `Upload failed: ${error.message}`
                );

            } finally {
                refreshButtons();
            }
        };


    /*
     * --------------------------------------------------
     * Physical device removal
     * --------------------------------------------------
     */

    function handleDisconnect(event) {
        if (
            event.target
            !== service.client.port
        ) {
            return;
        }

        setStateValue(
            "connected",
            false
        );

        deviceStatus.textContent =
            "Disconnected";

        setStatus(
            "Serial device disconnected."
        );

        refreshButtons();
    }


    navigator.serial?.addEventListener(
        "disconnect",
        handleDisconnect
    );


    refreshButtons();


    /*
     * --------------------------------------------------
     * Cleanup
     * --------------------------------------------------
     */

    return () => {
        navigator.serial?.removeEventListener(
            "disconnect",
            handleDisconnect
        );
    };
}
"""
