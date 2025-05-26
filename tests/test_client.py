from unittest.mock import MagicMock, call, patch

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

    client.at_command.assert_called_once_with("SP1")


def test_ignition(client):
    client.at_command.return_value = "ON"

    res = client.ignition()

    assert res == "ON"

    client.at_command.assert_called_once_with("IGN", wait_ready=False)


def test_scan_pid_support(client):
    client.obd_command.side_effect = [
        [
            [0x80, 0, 0, 1],
            [0x80, 0x10, 0, 1],
        ],
        [
            [0x80, 0, 0, 2],
            [0x80, 0x10, 0, 2],
        ],
    ]

    res = client.scan_pid_support()

    expect = [
        [1, 32, 33, 63],
        [1, 12, 32, 33, 44, 63],
    ]

    assert res == expect

    client.obd_command.assert_has_calls(
        [
            call(1, 0),
            call(1, 0x20),
        ]
    )


def test_scan_pid_support_no_ecus(client):
    client.obd_command.side_effect = [
        [],
    ]

    res = client.scan_pid_support()

    expect = []

    assert res == expect

    client.obd_command.assert_called_once_with(1, 0)
