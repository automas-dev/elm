import csv
from dataclasses import dataclass

PID_TABLE_PATH = "pid_table.csv"

_pid_table = None


@dataclass
class PID:
    pid: int
    data_bytes: int
    description: str
    min: str
    max: str
    units: str
    formula: str
    formula_raw: str


class PIDTable(list[PID]):
    def as_dict(self):
        if not hasattr(self, "_dict"):
            self._dict = {row.pid: row for row in self}
        return self._dict


def load_pid_table():
    global _pid_table

    if _pid_table is None:
        with open(PID_TABLE_PATH, "r", newline="") as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)

        headers = [h.lower().replace(" ", "_") for h in headers]

        table_data: list[dict[str, str | int]]
        table_data = list(map(lambda row: dict(zip(headers, row)), data))

        for row in table_data:
            row["pid"] = int(row["pid"])
            row["data_bytes"] = int(row["data_bytes"])

        _pid_table = PIDTable([PID(**row) for row in table_data])

    return _pid_table
