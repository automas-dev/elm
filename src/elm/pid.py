import csv

PID_TABLE_PATH = "pid_table.csv"


class PIDTable(list):
    def as_dict(self):
        if not hasattr(self, "_dict"):
            self._dict = {row["pid"]: row for row in self}
        return self._dict


def load_pid_table():
    with open(PID_TABLE_PATH, "r", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)

    headers = [h.lower().replace(" ", "_") for h in headers]

    return PIDTable(map(lambda row: dict(zip(headers, row)), data))
