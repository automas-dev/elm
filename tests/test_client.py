from unittest.mock import MagicMock, patch

import pytest

from elm import ElmClient


@pytest.fixture
def client():
    patcher = patch.object(ElmClient, "__bases__", (MagicMock,))
    with patcher:
        # See why is_local is needed https://stackoverflow.com/a/12220965
        patcher.is_local = True
        yield ElmClient()


def test_set_protocol(client):
    client.set_protocol(1)

    client.command.assert_called_once_with("AT SP 1")


def test_ignition(client):
    client.command.return_value = "ON"

    res = client.ignition()

    assert res == "ON"

    client.command.assert_called_once_with("AT IGN", wait_ready=False)


def test_scan_pid_support(client):
    client.read_until_ready.return_value = "PID1 \rPID2\r"

    res = client.scan_pid_support()

    assert res == ["PID1", "PID2"]

    client.command.assert_called_once_with(
        "01 00", expect="SEARCHING...", wait_ready=False
    )

    client.read_until_ready.assert_called_once()
