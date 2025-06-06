from unittest.mock import MagicMock, patch

import pytest

from elm import ElmClient

MOCK_KIA_PID_STR = [
    "41 00 80 00 00 01",
    "41 00 80 10 00 01",
    "41 00 80 00 00 01",
    "41 00 BE 3D A8 13",
    "41 00 80 00 00 01",
    "41 00 80 00 00 01",
]

MOCK_KIA_PID = [
    [1, 32],
    [1, 12, 32],
    [1, 32],
    [1, 3, 4, 5, 6, 7, 11, 12, 13, 14, 16, 17, 19, 21, 28, 31, 32],
    [1, 32],
    [1, 32],
]


@pytest.fixture
def client():
    patcher = patch.object(ElmClient, "__bases__", (MagicMock,))
    with patcher:
        # See why is_local is needed https://stackoverflow.com/a/12220965
        patcher.is_local = True
        yield ElmClient()
