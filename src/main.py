#!/usr/bin/env python3

from elm import ElmClient

if __name__ == "__main__":
    c = ElmClient("/dev/ttyUSB1")

    c.set_protocol(0)

    ign = c.ignition()
    print("Ignition is", ign)

    pid_support = c.scan_pid_support()
    print("Supported PID are", pid_support)
