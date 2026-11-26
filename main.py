#!/usr/bin/env python3
"""Entry program for 'The World in One Picture' (25 Nov 2026).

Validates the pre-rendered front page (entry.png, next to this file) and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR when set). No
network, no randomness: the output is byte-identical to the source on
every run.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")
MAX_BYTES = 1024 * 1024  # 1 MiB cap

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if not os.path.isfile(SRC):
        fail(f"entry.png not found next to main.py ({SRC})")
    with open(SRC, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the 1 MiB cap")
    if not data.startswith(PNG_SIGNATURE):
        fail("entry.png is not a PNG file")
    # Whole-image check: the file must end with a complete IEND chunk.
    if not data.endswith(b"IEND\xaeB`\x82"):
        fail("entry.png does not end with a complete IEND chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        fail(f"entry.png is {width}x{height}, expected 1024x1024")
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, OUT)
    digest = hashlib.sha256(data).hexdigest()
    # Read-back verification: the written file must hash exactly like the source.
    with open(OUT, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != digest:
        fail("read-back mismatch: /output/entry.png differs from entry.png")
    if len(written) != len(data):
        fail("read-back mismatch: /output/entry.png size differs")
    print(f"entry.png: {width}x{height}, {len(data)} bytes, sha256 {digest}")
    print(f"wrote {OUT} (verified identical on read-back)")


if __name__ == "__main__":
    main()
