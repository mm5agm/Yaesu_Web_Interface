import re
from .yaesu_cat import COMMANDS


def _hz_to_9ascii(hz: int) -> bytes:
    return f"{int(hz):09d}".encode("ascii")


def build_set_freq(vfo: str, hz: int) -> bytes:
    cmd = COMMANDS[vfo]["mnemonic"].encode("ascii")
    return cmd + _hz_to_9ascii(hz) + b";"


def build_get_freq(vfo: str) -> bytes:
    return COMMANDS[vfo]["mnemonic"].encode("ascii") + b";"


def parse_freq_response(resp: bytes) -> int:
    m = re.search(rb"(\d{9})", resp)
    if not m:
        raise ValueError("no 9-digit frequency found in response")
    return int(m.group(1))

