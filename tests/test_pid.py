from elm.pid import load_pid_table


def test_load_pid_table():
    table = load_pid_table()
    assert len(table) >= 1

    keys = list(table[0].keys())
    assert "PID" in keys
    assert "Data bytes" in keys
    assert "Description" in keys
    assert "Min" in keys
    assert "Max" in keys
    assert "Units" in keys
    assert "Formula" in keys
