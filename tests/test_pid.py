from elm.pid import load_pid_table


def test_load_pid_table():
    table = load_pid_table()
    assert len(table) >= 1


def test_load_pid_table_as_dict():
    table = load_pid_table()
    assert len(table) >= 1

    data = table.as_dict()

    for pid in map(lambda row: row.pid, table):
        assert pid in data.keys()
