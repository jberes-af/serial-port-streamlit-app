// /src/gui/streamlit/components/rp2040_device/frontend/rp2040_web_serial_service.js

const CTRL_A = 0x01;
const CTRL_B = 0x02;
const CTRL_C = 0x03;
const CTRL_D = 0x04;


export class RP2040WebSerialFileService {

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
                // Ignore.
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
            "Timed out waiting for device response."
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
                result.stderr
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

            entries.push({
                name,

                path:
                    this.joinRemotePath(
                        remoteDirectory,
                        name,
                    ),

                isDirectory,

                size:
                    isDirectory
                        ? null
                        : Number(sizeText),
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

                return (
                    a.name.localeCompare(
                        b.name
                    )
                );
            }
        );

        return entries;
    }


    async readFile(remotePath) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        const code = `
import binascii

_path = ${JSON.stringify(path)}

with open(_path, "rb") as _file:
    _data = _file.read()

print(
    binascii.b2a_base64(
        _data
    ).decode().strip()
)
`;

        const result =
            await this.execute(code);

        if (result.stderr.trim()) {
            throw new Error(
                result.stderr
            );
        }

        return this.base64ToBytes(
            result.stdout.trim()
        );
    }


    async writeLocalFile(
        file,
        remoteDirectory = "/",
    ) {
        const remotePath =
            this.joinRemotePath(
                remoteDirectory,
                file.name,
            );

        const buffer =
            await file.arrayBuffer();

        const bytes =
            new Uint8Array(buffer);

        await this.writeFile(
            remotePath,
            bytes,
        );

        return remotePath;
    }


    async writeFile(
        remotePath,
        bytes,
    ) {
        const path =
            this.normalizeRemotePath(
                remotePath
            );

        await this.execute(`
with open(
    ${JSON.stringify(path)},
    "wb"
) as _file:
    pass
`);

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
                    result.stderr
                );
            }
        }
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
                result.stderr
            );
        }
    }


    async createDirectory(
        remotePath,
    ) {
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
                result.stderr
            );
        }
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


    base64ToBytes(base64) {
        const binary =
            atob(base64);

        const bytes =
            new Uint8Array(
                binary.length
            );

        for (
            let i = 0;
            i < binary.length;
            i++
        ) {
            bytes[i] =
                binary.charCodeAt(i);
        }

        return bytes;
    }
}
