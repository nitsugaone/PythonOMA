#!/usr/bin/env python3
"""
CLI tool: parse a raw OMA CP PDU into structured layers.
Useful when you capture a real operator OTA via AT+CMGR.

Usage (hex string):
    python tools/parse_pdu.py --hex 060504 0b84 23f0 01060 ...

Usage (bin file):
    python tools/parse_pdu.py --file real_operator.bin
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from debug.pdu_parser import parse_pdu, print_parsed
from debug.pdu_diff import load_pdu_bin, load_pdu_hex


def main():
    parser = argparse.ArgumentParser(description="OMA CP PDU parser")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hex",  nargs="+", help="PDU as hex string(s)")
    group.add_argument("--file", help="PDU as raw .bin file")
    args = parser.parse_args()

    if args.hex:
        raw = load_pdu_hex(" ".join(args.hex))
    else:
        raw = load_pdu_bin(args.file)

    parsed = parse_pdu(raw)
    print_parsed(parsed)


if __name__ == "__main__":
    main()
