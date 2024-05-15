import re
import sys
import asyncio
import argparse
from typing import Awaitable, Callable, Any

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from rich.logging import RichHandler
from rich import traceback

import logging

logger: logging.Logger = logging.getLogger("searchCameras")
sh = RichHandler(rich_tracebacks=True, enable_link_path=True, show_time=False)
stream_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(message)s", datefmt="%H:%M:%S")
sh.setFormatter(stream_formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)

GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
GOPRO_BASE_URL = "http://10.5.5.9:8080"

noti_handler_T = Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None]]


def exception_handler(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception {str(loop)}: {msg}")
    logger.critical("This is unexpected and unrecoverable.")


async def connect_ble(notification_handler: noti_handler_T) -> BleakClient:
    asyncio.get_event_loop().set_exception_handler(exception_handler)

    # Scan for devices
    logger.info("Scanning for bluetooth devices...")

    RETRIES = 3
    for retry in range(RETRIES):
        # Map of discovered devices indexed by name
        devices: dict[str, BleakDevice] = {}

        # Scan callback to also catch nonconnectable scan responses
        # pylint: disable=cell-var-from-loop
        def _scan_callback(device: BleakDevice, _: Any) -> None:
            # Add to the dict if not unknown
            if device.name and device.name != "Unknown":
                devices[device.name] = device

        # Scan until we find devices
        matched_devices: list[BleakDevice] = []
        # Now get list of connectable advertisements
        for device in await BleakScanner.discover(timeout=3, detection_callback=_scan_callback):
            if device.name and device.name != "Unknown":
                devices[device.name] = device
        # Log every device we discovered
        for d in devices:
            logger.info(f"\tDiscovered: {d}")
        # Now look for our matching device(s)
        token = re.compile(r"GoPro [A-Z0-9]{4}")
        matched_devices = [device for name, device in devices.items() if token.match(name)]
        logger.info(f"Found {len(matched_devices)} matching devices.")



async def main() -> None:
    async def dummy_notification_handler(*_: Any) -> None: ...

    await connect_ble(dummy_notification_handler)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(e)
        sys.exit(-1)
    else:
        sys.exit(0)
