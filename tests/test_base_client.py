from unittest.mock import MagicMock, call, patch

import pytest

from elm.base_client import (
    ElmBaseClient,
    ElmClientError,
    ElmCommandError,
    ElmTimeout,
    ElmUnknownCommand,
    decode_obd,
    encode_obd,
)


@pytest.fixture
def mock_serial():
    yield MagicMock()


@pytest.fixture
def client(mock_serial):
    with patch("elm.base_client.ElmBaseClient.reset"):
        yield ElmBaseClient(connection=mock_serial)


def test_init_no_args():
    with pytest.raises(AssertionError, match="port or connection must be provided"):
        ElmBaseClient()


@patch("elm.base_client.ElmBaseClient.reset")
def test_init(mock_reset, mock_serial):
    client = ElmBaseClient(connection=mock_serial)

    assert not client._should_close

    assert mock_serial.timeout == 30

    mock_reset.assert_called_once()


@patch("elm.base_client.serial.Serial")
@patch("elm.base_client.ElmBaseClient.reset")
def test_init_port(mock_reset, mock_serial_cls, mock_serial):
    mock_serial_cls.return_value = mock_serial

    client = ElmBaseClient("port")

    assert client._should_close

    mock_serial_cls.assert_called_once_with(port="port", baudrate=38400)

    assert mock_serial.timeout == 30

    mock_reset.assert_called_once()


def test_enter_exit(client, mock_serial):
    with client as c:
        assert c == client

    mock_serial.close.assert_not_called()


def test_enter_exit_close(client, mock_serial):
    client._should_close = True

    with client as c:
        assert c == client

    mock_serial.close.assert_called_once()


@patch("elm.base_client.ElmBaseClient.at_command")
@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_reset(mock_write, mock_read, mock_wait, mock_at, mock_serial):
    mock_serial.read_until.return_value = b"status\r>"
    mock_read.return_value = "OK"

    ElmBaseClient(connection=mock_serial)

    mock_serial.flush.assert_called_once()
    mock_serial.read_all.assert_called_once()
    mock_serial.read_until.assert_called_once_with(b"\r>")

    mock_write.assert_has_calls(
        [
            call("AT Z"),
            call("AT E0"),
        ]
    )

    mock_read.assert_has_calls(
        [
            call("\r"),
            call("\r"),
        ]
    )

    mock_wait.assert_called_once()

    mock_at.assert_has_calls(
        [
            call("L0", expect="OK"),
            call("I"),
        ]
    )


@patch("elm.base_client.ElmBaseClient.write")
def test_reset_not_ready(mock_write, mock_serial):
    mock_serial.read_until.return_value = b""

    with pytest.raises(
        ElmClientError, match="Reset Failed: Device not ready after reset"
    ):
        ElmBaseClient(connection=mock_serial)

    mock_serial.flush.assert_called_once()
    mock_serial.read_all.assert_called_once()
    mock_serial.read_until.assert_called_once_with(b"\r>")

    mock_write.assert_called_once_with("AT Z")


@patch("elm.base_client.ElmBaseClient.at_command")
@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_reset_e0_not_ok(mock_write, mock_read, mock_wait, mock_at, mock_serial):
    mock_serial.read_until.return_value = b"status\r>"
    mock_read.return_value = "NO"

    with pytest.raises(
        ElmClientError, match="Reset Failed: AT E0 command returned 'NO'"
    ):
        ElmBaseClient(connection=mock_serial)

    mock_serial.flush.assert_called_once()
    mock_serial.read_all.assert_called_once()
    mock_serial.read_until.assert_called_once_with(b"\r>")

    mock_write.assert_has_calls(
        [
            call("AT Z"),
            call("AT E0"),
        ]
    )

    mock_read.assert_has_calls(
        [
            call("\r"),
            call("\r"),
        ]
    )

    mock_wait.assert_not_called()
    mock_at.assert_not_called()


def test_write(client, mock_serial):
    client.write("cmd", append_cr=False)

    mock_serial.write.assert_called_once_with(b"cmd")


def test_write_append_cr(client, mock_serial):
    client.write("cmd", append_cr=True)

    mock_serial.write.assert_has_calls(
        [
            call(b"cmd"),
            call(b"\r"),
        ]
    )


def test_write_append_not_needed(client, mock_serial):
    client.write("cmd\r", append_cr=True)

    mock_serial.write.assert_called_once_with(b"cmd\r")


def test_read_until(client, mock_serial):
    mock_serial.read_until.return_value = b"retend"

    res = client.read_until("end")

    assert res == "ret"

    mock_serial.read_until.assert_called_once_with(b"end")


def test_read_until_not_enough(client, mock_serial):
    mock_serial.read_until.return_value = b"r"

    with pytest.raises(ElmTimeout, match="Timeout while waiting for end"):
        client.read_until("end")


def test_read_until_no_end(client, mock_serial):
    mock_serial.read_until.return_value = b"retret"

    with pytest.raises(ElmTimeout, match="Timeout while waiting for end"):
        client.read_until("end")


@patch("elm.base_client.ElmBaseClient.read_until")
def test_read_until_ready(mock_read, client):
    mock_read.return_value = "ret"

    res = client.read_until_ready()

    assert res == "ret"

    mock_read.assert_called_once_with("\r>")


@patch("elm.base_client.logger.warning")
@patch("elm.base_client.ElmBaseClient.read_until_ready")
def test_wait_until_ready(mock_read, mock_log, client):
    mock_read.return_value = ""

    client.wait_until_ready()

    mock_read.assert_called_once()

    mock_log.assert_not_called()


@patch("elm.base_client.logger.warning")
@patch("elm.base_client.ElmBaseClient.read_until_ready")
def test_wait_until_ready_extra_response(mock_read, mock_log, client):
    mock_read.return_value = "extra"

    client.wait_until_ready()

    mock_read.assert_called_once()

    mock_log.assert_called_once_with("Unhandled response {!r}", "extra")


@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_at_command(mock_write, mock_read, mock_wait, client):
    client.at_command("cmd")

    mock_write.assert_called_once_with("ATcmd")

    mock_read.assert_called_once_with("\r")

    mock_wait.assert_called()


@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_at_command_no_wait(mock_write, mock_read, mock_wait, client):
    client.at_command("cmd", wait_ready=False)

    mock_write.assert_called_once_with("ATcmd")

    mock_read.assert_called_once_with("\r")

    mock_wait.assert_not_called()


@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_at_command_expect(mock_write, mock_read, mock_wait, client):
    mock_read.return_value = "ret"

    with pytest.raises(
        ElmCommandError, match="Command 'cmd' returned 'ret' expected 'expected"
    ):
        client.at_command("cmd", expect="expected")

    mock_write.assert_called_once_with("ATcmd")

    mock_read.assert_called_once_with("\r")

    mock_wait.assert_not_called()


@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_at_command_unknown_command(mock_write, mock_read, mock_wait, client):
    mock_read.return_value = "?"

    with pytest.raises(ElmClientError, match="Unknown command 'cmd'"):
        client.at_command("cmd")

    mock_write.assert_called_once_with("ATcmd")

    mock_read.assert_called_once_with("\r")

    mock_wait.assert_not_called()


@patch("elm.base_client.ElmBaseClient.wait_until_ready")
@patch("elm.base_client.ElmBaseClient.read_until")
@patch("elm.base_client.ElmBaseClient.write")
def test_at_command_empty(mock_write, mock_read, mock_wait, client):
    with pytest.raises(ValueError, match="Empty command"):
        client.at_command("")

    mock_write.assert_not_called()
    mock_read.assert_not_called()
    mock_wait.assert_not_called()


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command(mock_write, mock_read, client):
    mock_read.return_value = "41 02 11 22 33 44"
    res = client.obd_command(1, 2)

    assert res == [[0x11, 0x22, 0x33, 0x44]]

    mock_write.assert_called_once_with("01 02")

    mock_read.assert_called_once()


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_no_read_data(mock_write, mock_read, client):
    mock_read.return_value = "41 02"
    res = client.obd_command(1, 2)

    assert res == [[]]

    mock_write.assert_called_once_with("01 02")

    mock_read.assert_called_once()


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_multi_response(mock_write, mock_read, client):
    mock_read.return_value = "41 02 11 \r41 02 22\r"
    res = client.obd_command(1, 2)

    assert res == [[0x11], [0x22]]

    mock_write.assert_called_once_with("01 02")

    mock_read.assert_called_once()


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_write_data(mock_write, mock_read, client):
    client.obd_command(1, 2, [4, 5])

    mock_write.assert_called_once_with("01 02 04 05")


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_not_enough_response(mock_write, mock_read, client):
    mock_read.return_value = ""

    with pytest.raises(ElmClientError, match="Invalid format for obd response ''"):
        client.obd_command(1, 2)

    mock_read.return_value = "01"

    with pytest.raises(
        ElmClientError,
        match="Response 0 has not enough values, need at least mode and pid",
    ):
        client.obd_command(1, 2)


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_wrong_mode_or_pid(mock_write, mock_read, client):
    mock_read.return_value = "42 02"

    with pytest.raises(
        ElmClientError,
        match="Response 0 was not for the current command, got mode 42 pid 02",
    ):
        client.obd_command(1, 2)

    mock_read.return_value = "41 03"

    with pytest.raises(
        ElmClientError,
        match="Response 0 was not for the current command, got mode 41 pid 03",
    ):
        client.obd_command(1, 2)


@patch("elm.base_client.ElmBaseClient.read_until_ready")
@patch("elm.base_client.ElmBaseClient.write")
def test_obd_command_fail_search(mock_write, mock_read, client):
    mock_read.return_value = "SEARCHING...\rUNABLE TO CONNECT"

    with pytest.raises(ElmClientError, match="Unable to connect"):
        client.obd_command(1, 2)


def test_encode_obd():
    assert encode_obd([]) == ""
    assert encode_obd([1]) == "01"
    assert encode_obd([1, 0x41]) == "01 41"

    with pytest.raises(
        AssertionError, match="Data values must each be a 2 digit positive hex value"
    ):
        encode_obd([0x100])


def test_decode_obd():
    assert decode_obd("01") == [1]
    assert decode_obd("01 41") == [1, 0x41]

    with pytest.raises(ValueError, match="Invalid format for obd response ''"):
        decode_obd("")

    with pytest.raises(ValueError, match="Invalid format for obd response '100'"):
        decode_obd("100")

    with pytest.raises(ValueError, match="Invalid format for obd response 'G'"):
        decode_obd("G")
