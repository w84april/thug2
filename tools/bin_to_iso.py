"""Convert a single MODE1/2352 data track to ISO; never modifies the source."""

import argparse
from pathlib import Path
import tempfile

SYNC = b"\x00" + b"\xff" * 10 + b"\x00"


def convert(source, destination):
    if source.stat().st_size % 2352:
        raise ValueError("Incomplete 2352-byte sector")
    with source.open("rb") as src, destination.open("xb") as dst:
        while sector := src.read(2352):
            if sector[:12] != SYNC or sector[15] != 1:
                raise ValueError("Expected a MODE1/2352 data sector")
            dst.write(sector[16:2064])


def self_test():
    with tempfile.TemporaryDirectory() as directory:
        src, dst = Path(directory) / "test.bin", Path(directory) / "test.iso"
        payload = bytes(range(256)) * 8
        src.write_bytes((SYNC + b"\x00\x02\x00\x01" + payload + bytes(288)) * 2)
        convert(src, dst)
        assert dst.read_bytes() == payload * 2
        src.write_bytes(b"truncated")
        try:
            convert(src, Path(directory) / "bad.iso")
        except ValueError:
            pass
        else:
            raise AssertionError("Incomplete sectors must be rejected")
    print("Conversion checks passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path)
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.source and args.destination:
        convert(args.source, args.destination)
    else:
        parser.error("Provide source and destination, or --self-test")
