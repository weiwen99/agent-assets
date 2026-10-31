#!/usr/bin/env python3
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(74)


def validate(path: Path, expected_width: int) -> tuple[int, int]:
    payload = path.read_bytes()
    if not payload.startswith(PNG_SIGNATURE):
        fail(f"Not a PNG file: {path}")

    offset = len(PNG_SIGNATURE)
    ihdr: bytes | None = None
    idat_parts: list[bytes] = []
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        chunk_type = payload[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > len(payload):
            fail(f"Truncated PNG chunk in {path}")
        chunk_data = payload[data_start:data_end]
        if chunk_type == b"IHDR":
            ihdr = chunk_data
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break
        offset = data_end + 4

    if ihdr is None or len(ihdr) != 13:
        fail(f"Missing or malformed IHDR in {path}")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", ihdr)
    if width != expected_width:
        fail(f"Unexpected PNG width: got {width}, expected {expected_width}")
    if height <= 0:
        fail("PNG height must be positive")
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 2, 0, 0, 0):
        fail(
            "PNG must be non-interlaced 8-bit RGB: "
            f"got bit_depth={bit_depth}, color_type={color_type}, "
            f"compression={compression}, filter={filter_method}, interlace={interlace}"
        )
    if not idat_parts:
        fail(f"Missing IDAT in {path}")

    try:
        raw = zlib.decompress(b"".join(idat_parts))
    except zlib.error as error:
        fail(f"Cannot decompress PNG pixels: {error}")
    if len(raw) < 4:
        fail(f"PNG has no complete first pixel: {path}")

    filter_type = raw[0]
    if filter_type not in range(5):
        fail(f"Unknown PNG row filter: {filter_type}")
    first_rgb = tuple(raw[1:4])
    if first_rgb != (255, 255, 255):
        fail(f"Top-left page pixel must be white RGB; got {first_rgb}")

    return width, height


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} FILE.png EXPECTED_WIDTH", file=sys.stderr)
        raise SystemExit(64)
    path = Path(sys.argv[1])
    try:
        expected_width = int(sys.argv[2])
    except ValueError:
        print(f"EXPECTED_WIDTH must be an integer: {sys.argv[2]}", file=sys.stderr)
        raise SystemExit(64)
    width, height = validate(path, expected_width)
    print(f"Validated {path}: {width}x{height}, 8-bit RGB, white page")


if __name__ == "__main__":
    main()
