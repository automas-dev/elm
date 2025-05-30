from loguru import logger

from .base_client import ElmBaseClient
from .pid import load_pid_table


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

    def scan_pid_support(self) -> list[int]:
        logger.info("Searching for supported PID")

        resp = self.obd_command(1, 0)
        logger.debug("Found {} ecus", len(resp))

        pids = set()
        for ecu in map(bitmask_to_pids, resp):
            pids = pids.union(set(ecu))

        if len(pids) == 0:
            logger.warning("Could not find any supported PIDs")
            return []

        for extra in [0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0]:
            if extra not in pids:
                break

            logger.debug("Extending PID with range {:02X}", extra)

            resp = self.obd_command(1, extra)

            for ecu in map(lambda x: bitmask_to_pids(x, extra), resp):
                pids = pids.union(set(ecu))

        return sorted(pids)


def map_ecu_pids(ecu: list[int]):
    pid_table = load_pid_table()
    pid_map = pid_table.as_dict()

    ecu_map = {pid: pid_map[pid] for pid in ecu}

    return ecu_map
