#!/usr/bin/env python3
"""Entry program for the 25 November 2026 news image.

Validates entry.png (PNG signature, IEND terminator, 1024x1024 pixels,
at most 1 MiB) and copies it byte-for-byte to the output directory
the harness expects.

Run:  python3 main.py                 (validates + copies to /output)
      python3 main.py --verify-only   (validates only, copies nothing)
      python3 main.py --self-test     (validates a synthetic 1x1 PNG)

Output directory: $MAKEFUN_OUTPUT_DIR when set, otherwise /output.
The entry image lives next to this file. Standard library only, no
network access, deterministic.
"""

import argparse
import hashlib
import os
import struct
import sys
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_PATH = os.path.join(HERE, "entry.png")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def read_png_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def check_signature(data):
    if data[:8] != PNG_SIGNATURE:
        return "first 8 bytes are not the PNG signature"
    return None


def check_dimensions(data):
    if len(data) < 33:
        return "file too short to hold an IHDR chunk"
    if data[12:16] != b"IHDR":
        return "first chunk is not IHDR"
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return (f"image is {width}x{height}, "
                f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}")
    return None


def check_terminator(data):
    if len(data) < 12:
        return "file too short to hold an IEND chunk"
    if data[-12:-8] != b"\x00\x00\x00\x00" or data[-8:-4] != b"IEND":
        return "file does not end with an IEND chunk"
    if data[-4:] != struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF):
        return "IEND chunk has a bad CRC"
    return None


def validate(path):
    """Return a list of problems found in the PNG at `path` (empty = valid)."""
    problems = []
    try:
        data = read_png_bytes(path)
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]
    if len(data) > MAX_BYTES:
        problems.append(f"file is {len(data)} bytes, over the 1 MiB cap")
    for check in (check_signature, check_dimensions, check_terminator):
        problem = check(data)
        if problem:
            problems.append(problem)
    return problems


def copy_entry(data, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as handle:
        handle.write(data)
    return out_path


def self_test():
    """Build a minimal 1x1 red PNG in memory and run the validators on it."""
    raw = b"\x00\xff\x00\x00"  # one scanline: filter 0 + RGB red
    def chunk(kind, payload):
        body = kind + payload
        return (struct.pack(">I", len(payload)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png = (PNG_SIGNATURE + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    problems = []
    for check in (check_signature, check_terminator):
        problem = check(png)
        if problem:
            problems.append(problem)
    # Dimensions are expected to fail here (1x1, not 1024x1024); that
    # failure is the point — it proves the dimension check fires.
    dim_problem = check_dimensions(png)
    if dim_problem is None:
        problems.append("dimension check did not flag the 1x1 test image")
    if problems:
        print("self-test FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("self-test passed: signature + IEND checks accept a valid PNG, "
          "dimension check rejects 1x1")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true",
                        help="validate entry.png without copying it")
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in validator self-test")
    parser.add_argument("--out", default=None,
                        help="output directory (overrides "
                             "$MAKEFUN_OUTPUT_DIR and /output)")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    problems = validate(ENTRY_PATH)
    if problems:
        print(f"entry.png FAILED validation ({ENTRY_PATH}):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    data = read_png_bytes(ENTRY_PATH)
    print(f"entry.png OK: {len(data)} bytes, "
          f"1024x1024, sha256 {sha256_hex(data)}")
    if args.verify_only:
        return 0

    out_dir = (args.out or os.environ.get("MAKEFUN_OUTPUT_DIR")
               or "/output")
    out_path = copy_entry(data, out_dir)
    copied = read_png_bytes(out_path)
    if sha256_hex(copied) != sha256_hex(data):
        print(f"ERROR: copy at {out_path} differs from entry.png",
              file=sys.stderr)
        return 1
    # Re-validate the copy itself, so a bad write cannot slip through.
    copy_problems = validate(out_path)
    if copy_problems:
        print(f"ERROR: copied file at {out_path} failed validation:")
        for problem in copy_problems:
            print(f"  - {problem}")
        return 1
    print(f"copied to {out_path} (sha256 verified identical, "
          f"re-validated OK)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
