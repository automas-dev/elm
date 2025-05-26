from loguru import logger

from .base_client import ElmBaseClient


def bitmask_to_pids(bitmask: list[int], offset: int = 0):
    mask = [x[2:].zfill(8) for x in map(bin, bitmask)]
    pids = [1 + i + offset for i, c in enumerate("".join(mask)) if c == "1"]
    return pids


class ElmClient(ElmBaseClient):
    def set_protocol(self, protocol: int = 0):
        logger.info("Set protocol to {}", protocol)
        self.at_command(f"SP{protocol}")

    def ignition(self):
        logger.info("Check ignition status")

        ign = self.at_command("IGN", wait_ready=False)
        logger.debug("Ignition status return {}", ign)

        self.wait_until_ready()

        return ign

    def scan_pid_support(self):
        logger.info("Searching for supported PID")

        resp = self.obd_command(1, 0)
        logger.debug("Found {} ecus", len(resp))

        ecu_map = list(map(bitmask_to_pids, resp))

        if len(ecu_map) == 0:
            return ecu_map

        for extra in [0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0]:
            if extra not in ecu_map[0]:
                break

            logger.debug("Extending PID with range {:02X}", extra)

            resp = self.obd_command(1, extra)
            ecu_extra_map = [bitmask_to_pids(data, extra) for data in resp]

            for ecu, extra in zip(ecu_map, ecu_extra_map):
                ecu.extend(extra)

        return ecu_map
