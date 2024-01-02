#!/usr/bin/env python3

"""
Implements a Master Boot Record (MBR, LBA=0) parser.

I extensively use [Paul Stoffregen's blog post](https://www.pjrc.com/tech/8051/ide/fat32.html)
to develop this module -- thank you!
"""

import struct
from dataclasses import dataclass


class FaultyMBRError(Exception):
    """The MBR is not valid."""


class InvalidMBRSizeError(Exception):
    """The provided MBR is not 512 bytes. Did you use LBA = 0?"""


@dataclass
class PartitionEntry:
    """MBR Partition Entry"""

    type_code: int  # TODO: change to enum type
    lba_begin: int


@dataclass
class MasterBootRecord:
    """Master Boot Record"""

    boot_code: bytes
    partitions: list[PartitionEntry]


def parse_partition_entry(partition_entry_bytes: bytes) -> PartitionEntry:
    """Parses a partition entry, retrieves the type code and LBA begin address."""
    return PartitionEntry(*struct.unpack("<4xB3xI4x", partition_entry_bytes))


def create_mbr(mbr_bytes: bytes) -> MasterBootRecord:
    """Creates a MBR class instance from the first disk sector (MBA sector)."""
    if len(mbr_bytes) != 512:
        raise InvalidMBRSizeError
    if mbr_bytes[510:512] != b"\x55\xAA":
        raise FaultyMBRError

    boot_code, *partitions_bytes = struct.unpack("<446s16s16s16s16s2x", mbr_bytes)
    partitions = [
        parse_partition_entry(partition_entry) for partition_entry in partitions_bytes
    ]
    return MasterBootRecord(boot_code, partitions)
