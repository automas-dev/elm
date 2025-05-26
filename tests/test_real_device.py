from time import sleep
from unittest.mock import patch

import pytest
from serial import Serial

from elm import ElmClient
from elm.base_client import ELM_BAUD

TTY_ADDR = "/dev/ttyUSB1"


@pytest.fixture
def client():
    with ElmClient(TTY_ADDR) as c:
        yield c


@pytest.fixture
def raw():
    with Serial(TTY_ADDR, ELM_BAUD) as s:
        yield s


# def test_buffer_empty_after_init(client):
#     assert client.id == "ELM327 v1.5"
#     sleep(1)
#     res = client._con.read_all()
#     assert len(res) == 0


# def test_at_z(raw):
#     raw.write(b"ATZ\r")
#     status = raw.read_until(b">")

#     if status.startswith(b"ATZ"):
#         assert status == b"ATZ\r\r\rELM327 v1.5\r\r>"

#     # if echo is disabled before reset
#     else:
#         assert status == b"\r\rELM327 v1.5\r\r>"

#     sleep(1)

#     # Nothing is left in the read buffer
#     more = raw.read_all()
#     assert len(more) == 0


# def test_at_e0(raw):
#     raw.write(b"ATZ\r")
#     raw.read_until(b">")

#     raw.write(b"ATE0\r")
#     echo = raw.read_until(b"\r")
#     assert echo == b"ATE0\r"

#     status = raw.read_until(b"\r")
#     assert status == b"OK\r"

#     wait = raw.read_until(b">")
#     assert wait == b"\r>"

#     sleep(1)

#     # Nothing is left in the read buffer
#     more = raw.read_all()
#     assert len(more) == 0
