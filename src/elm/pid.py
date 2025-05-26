KIA_PIDS = {
    0x00: {
        "name": "PID SUPPORT",
        "description": "PIDs supported [$01 - $20]",
        "n_bytes": 4,
    },
    0x01: {
        "name": "MONITOR STATUS",
        "description": "Monitor status since DTCs cleared. (Includes malfunction indicator lamp (MIL), status and number of DTCs, components tests, DTC readiness checks)",
        "n_bytes": 4,
    },
    0x03: {
        "name": "FUEL SYSTEM STATUS",
        "description": "Fuel system status",
        "n_bytes": 2,
    },
    0x04: {
        "name": "CALCULATED ENGINE LOAD",
        "description": "Calculated engine load",
        "n_bytes": 1,
    },
    0x05: {
        "name": "ENGINE COOLANT TEMP",
        "description": "Engine coolant temperature",
        "n_bytes": 1,
    },
    0x06: {
        "name": "",
        "description": "Short term fuel trim (STFT)—Bank 1",
        "n_bytes": 1,
    },
    0x07: {
        "name": "",
        "description": "Long term fuel trim (LTFT)—Bank 1",
        "n_bytes": 1,
    },
    0x0B: {
        "name": "",
        "description": "Intake manifold absolute pressure	",
        "n_bytes": 2,
    },
    0x0C: {
        "name": "",
        "description": "Engine speed",
        "n_bytes": 2,
    },
    0x0D: {
        "name": "",
        "description": "Vehicle speed",
        "n_bytes": 2,
    },
    0x0E: {
        "name": "",
        "description": "Timing advance",
        "n_bytes": 2,
    },
    0x10: {
        "name": "",
        "description": "Mass air flow sensor (MAF) air flow rate",
        "n_bytes": 2,
    },
    0x11: {
        "name": "",
        "description": "Throttle position",
        "n_bytes": 2,
    },
    0x13: {
        "name": "",
        "description": "Oxygen sensors present (in 2 banks)",
        "n_bytes": 2,
    },
    0x15: {
        "name": "",
        "description": "Oxygen Sensor 2 A: Voltage B: Short term fuel trim",
        "n_bytes": 2,
    },
    0x1C: {
        "name": "",
        "description": "OBD standards this vehicle conforms to",
        "n_bytes": 2,
    },
    0x1F: {
        "name": "",
        "description": "Run time since engine start",
        "n_bytes": 2,
    },
    0x20: {
        "name": "",
        "description": "PIDs supported [$21 - $40]",
        "n_bytes": 2,
    },
}
