# log_battery.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed, Sep  1, 2021  5:05:45 PM

"""Example to continuously read the battery (with no Wifi connection)"""

import argparse
import asyncio
import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from open_gopro import WirelessGoPro, types
from open_gopro.constants import StatusId
from open_gopro.logger import set_stream_logging_level, setup_logging
from open_gopro.util import add_cli_args_and_parse, ainput

console = Console()

async def main(args: argparse.Namespace) -> None:
    logger = setup_logging(__name__, args.log)

    gopro: Optional[WirelessGoPro] = None
    async with WirelessGoPro(args.identifier, enable_wifi=True) as gopro:
        set_stream_logging_level(logging.ERROR)
        with console.status("[bold green]Polling the battery until it dies..."):
            PER = (await gopro.ble_status.int_batt_per.get_value()).data
            BAR = (await gopro.ble_status.batt_level.get_value()).data
            console.print(f"Camera battarey as {PER}")
        console.print("Exiting...")

    if gopro:
        await gopro._close_wifi()
        await gopro.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Connect to the GoPro via BLE only and continuously read the battery (either by polling or notifications)."
    )
    parser.add_argument(
        "-p",
        "--poll",
        type=int,
        help="Set to poll the battery at a given interval. If not set, battery level will be notified instead. Defaults to notifications.",
        default=None,
    )
    return add_cli_args_and_parse(parser, wifi=False)


def entrypoint() -> None:
    asyncio.run(main(parse_arguments()))


if __name__ == "__main__":
    entrypoint()
