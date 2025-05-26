from elm.pid import load_pid_table


def test_load_pid_table():
    table = load_pid_table()
    assert len(table) >= 1

    keys = list(table[0].keys())
    assert "pid" in keys
    assert "data_bytes" in keys
    assert "description" in keys
    assert "min" in keys
    assert "max" in keys
    assert "units" in keys
    assert "formula" in keys


def test_load_pid_table_as_dict():
    table = load_pid_table()
    assert len(table) >= 1

    data = table.as_dict()

    for pid in map(lambda row: row["pid"], table):
        assert pid in data.keys()

    row = data[table[0]["pid"]]
    keys = list(row.keys())

    assert "pid" in keys
    assert "data_bytes" in keys
    assert "description" in keys
    assert "min" in keys
    assert "max" in keys
    assert "units" in keys
    assert "formula" in keys
