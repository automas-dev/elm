import re

import serial
from loguru import logger

ELM_BAUD = 38400
ELM_READ_TIMEOUT = 30  # s

ELM_READY_BYTES = "\r>"
CR = "\r"

DATA_PATTERN_RE = re.compile(r"[0-9a-fA-F]{2}( [0-9a-fA-F]{2})*")


def encode_obd(data: list[int]):
    values = []

    for x in data:
        assert 0 <= x <= 0xFF, "Data values must each be a 2 digit positive hex value"
        values.append(f"{x:02X}")

    return " ".join(values)


def decode_obd(text: str):
    if not DATA_PATTERN_RE.fullmatch(text):
        raise ValueError(f"Invalid format for obd response {text!r}")

    values = text.strip().split(" ")
    data = [int(v, 16) for v in values]

    return data


class ElmClientError(RuntimeError):
    pass


class ElmUnknownCommand(ElmClientError):
    pass


class ElmCommandError(ElmClientError):
    def __init__(self, cmd: str, resp: str, expect: str):
        super().__init__(f"Command {cmd!r} returned {resp!r} expected {expect!r}")


class ElmTimeout(ElmClientError):
    def __init__(self, expect: str):
        super().__init__(f"Timeout while waiting for {expect}")


class ElmBaseClient:
    def __init__(
        self, port: str | None = None, connection: serial.Serial | None = None
    ):
        assert (
            port is not None or connection is not None
        ), "port or connection must be provided"

        if connection is not None:
            logger.info("Opening client with existing serial connection")
            self._con = connection
            self._should_close = False

        else:
            logger.info("Opening client with new serial connection to port {}", port)
            self._con = serial.Serial(port=port, baudrate=ELM_BAUD)
            self._should_close = True

        self._con.timeout = ELM_READ_TIMEOUT

        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        if self._should_close:
            self._con.close()

    def reset(self):
        """Reset the device and disable echo / line feed."""
        logger.debug("Reset device")

        # Clear i/o
        self._con.flush()
        self._con.read_all()

        # Reset device
        self.write("AT Z")

        # Wait until device is ready, raw read because first boot of elm can
        # return garbage bytes that utf-8 fails to decode
        status = self._con.read_until(b"\r>")
        if len(status) < 2 or not status.endswith(b"\r>"):
            raise ElmClientError("Reset Failed: Device not ready after reset")

        # Disable echo
        self.write("AT E0")
        # Discard echo of command
        self.read_until(CR)

        # Read result of command
        e0_ret = self.read_until(CR)
        logger.debug("Disable echo returns is {!r}", e0_ret)

        # Check command was successful
        if e0_ret != "OK":
            raise ElmClientError(f"Reset Failed: AT E0 command returned {e0_ret!r}")

        self.wait_until_ready()

        # Disable line feed, use command because echo is now disabled and expect= can work
        self.at_command("AT L0", expect="OK")

        self.id = self.at_command("AT I")
        logger.info("Device is {}", self.id)

    def write(self, b: str, append_cr=True):
        """Convert b to bytes and write it to the serial device."""
        self._con.write(b.encode())
        if append_cr and not b.endswith(CR):
            self._con.write(b"\r")

    def read_until(self, expect: str = CR):
        """Read until expect is found or timeout occurs."""
        resp = self._con.read_until(expect.encode())
        resp = resp.decode()

        if len(resp) < len(expect) or not resp.endswith(expect):
            raise ElmTimeout(expect)

        resp = resp[: -len(expect)]

        return resp

    def read_until_ready(self):
        """Read until device ready bytes are read."""
        resp = self.read_until(ELM_READY_BYTES)
        return resp

    def wait_until_ready(self):
        """Wait for device ready bytes, warning if any unhandled response is found."""
        resp = self.read_until_ready()

        if len(resp) > 0:
            logger.warning("Unhandled response {!r}", resp)

    def at_command(self, cmd: str, expect: str | None = None, wait_ready=True):
        """Send a command and receive it's response."""
        if len(cmd) == 0:
            raise ValueError("Empty command")

        logger.debug("Send AT command {!r}", cmd)

        self.write(f"AT{cmd}")

        resp = self.read_until(CR)

        logger.debug("Response to command {!r} is {!r}", cmd, resp)

        if resp == "?":
            raise ElmUnknownCommand(cmd)

        if expect is not None and resp != expect:
            raise ElmCommandError(cmd, resp, expect)

        if wait_ready:
            self.wait_until_ready()

        return resp

    def obd_command(self, mode: int, pid: int, data: list[int] | None = None):
        assert 0 <= mode <= 0xFF, "Mode should be a 2 digit positive hex value"
        assert 0 <= pid <= 0xFF, "pid should be a 2 digit positive hex value"

        if data is not None:
            cmd = [mode, pid, *data]

        else:
            cmd = [mode, pid]

        self.write(encode_obd(cmd))

        resp_str = self.read_until_ready()
        lines = resp_str.strip().split(CR)

        try:
            resp = list(map(decode_obd, lines))

        except ValueError as e:
            raise ElmClientError(str(e)) from e

        expect_mode = 0x40 + mode

        for i, r in enumerate(resp):
            if len(r) < 2:
                raise ElmClientError(
                    f"Response {i} has not enough values, need at least mode and pid"
                )

            if r[0] != expect_mode or r[1] != pid:
                raise ElmClientError(
                    f"Response {i} was not for the current command, got mode {r[0]:02X} pid {r[1]:02X}"
                )

            # Remove mode and pid of response
            resp[i] = r[2:]

        return resp
