#!/usr/bin/env python3

import json

from elm import ElmClient

if __name__ == "__main__":
    c = ElmClient("/dev/ttyUSB1")

    c.set_protocol(0)

    ign = c.ignition()
    print("Ignition is", ign)

    pid_support = c.scan_pid_support()
    print("Supported PID are", pid_support)

    # Read supported by all
    all_support_data = {}
    for pid in pid_support:
        data = c.obd_command(1, pid, return_raw=True)
        all_support_data[pid] = data

    print(all_support_data)

    with open("kia_pid_01_dump.json", "w") as f:
        json.dump(all_support_data, f, indent=2)
