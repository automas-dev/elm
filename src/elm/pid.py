import csv

PID_TABLE_PATH = "pid_table.csv"


def load_pid_table():
    with open(PID_TABLE_PATH, "r", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)

    return [dict(zip(headers, row)) for row in data]
