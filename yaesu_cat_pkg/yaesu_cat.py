COMMANDS = {
    "FA": {"mnemonic": "FA", "param_count": 9, "desc": "Frequency main band"},
    "FB": {"mnemonic": "FB", "param_count": 9, "desc": "Frequency sub band"},
}


def build_get_freq(vfo: str) -> bytes:
    """Build the "get frequency" command for the given VFO.

    Example: build_get_freq('FA') -> b'FA;'
    """
    if vfo not in COMMANDS:
        raise ValueError(f"Unknown VFO: {vfo}")
    return f"{vfo};".encode("ascii")


def build_set_freq(vfo: str, hz: int) -> bytes:
    """Build the "set frequency" command for the given VFO and frequency in Hz.

    The radio expects a 9-digit, zero-padded integer frequency (Hz) immediately
    following the two-letter VFO mnemonic, terminated with a semicolon.

    Example: build_set_freq('FA', 14100000) -> b'FA014100000;'
    """
    if vfo not in COMMANDS:
        raise ValueError(f"Unknown VFO: {vfo}")
    try:
        hz_int = int(hz)
    except Exception:
        raise ValueError("hz must be an integer number of Hz")
    return f"{vfo}{hz_int:09d};".encode("ascii")


import re


def parse_freq_response(resp: bytes) -> int:
    """Parse a frequency response from the radio and return Hz as int.

    Looks for the first 9-digit group in the response bytes and returns it as
    an integer. Raises ValueError if no 9-digit frequency is found.
    """
    if not isinstance(resp, (bytes, bytearray)):
        raise TypeError("resp must be bytes or bytearray")
    m = re.search(rb"(\d{9})", resp)
    if not m:
        raise ValueError("no 9-digit frequency found in response")
    return int(m.group(1))
