import re

from loguru import logger

from .base_client import CR, ElmBaseClient, ElmClientError


def bitmask_to_pids(bitmask: list[int], offset: int = 0):
    mask = [x[2:].zfill(8) for x in map(bin, bitmask)]
    pids = [1 + i + offset for i, c in enumerate("".join(mask)) if c == "1"]
    return pids


class ElmClient(ElmBaseClient):
    def set_protocol(self, protocol: int = 0):
        logger.info("Set protocol to {}", protocol)
        self.at_command(f"AT SP {protocol}")

    def ignition(self):
        logger.info("Check ignition status")

        ign = self.at_command("AT IGN", wait_ready=False)
        logger.debug("Ignition status return {}", ign)

        self.wait_until_ready()

        return ign

    def scan_pid_support(self):
        logger.info("Searching for supported PID")

        self.at_command("01 00", expect="SEARCHING...", wait_ready=False)

        resp = self.read_until_ready().strip()
        ecus = list(map(str.strip, resp.split("\r")))
        logger.debug("Found {} ecus", len(ecus))

        ecu_map = []
        for ecu in ecus:
            mask_ints = [int(x, 16) for x in ecu.split(" ")]
            assert mask_ints[0] == 0x41
            assert mask_ints[1] == 0
            pids = bitmask_to_pids(mask_ints[2:])
            ecu_map.append(pids)

        for extra in [0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0]:
            if extra not in ecu_map[0]:
                break

            logger.debug("Extending PID with range {:02X}", extra)

            extra_str = hex(extra)[2:]
            assert len(extra_str) == 2
            self.at_command(f"01 {extra_str}", expect="SEARCHING...", wait_ready=False)

            resp = self.read_until_ready().strip()
            ecus = list(map(str.strip, resp.split("\r")))
            logger.debug("Found {} ecus", len(ecus))

            for ecu, ecu_list in zip(ecus, ecu_map):
                mask_ints = [int(x, 16) for x in ecu.split(" ")]
                assert mask_ints[0] == 0x41
                assert mask_ints[1] == 0
                pids = bitmask_to_pids(mask_ints[2:], extra)
                ecu_list.extend(pids)

        return ecu_map
