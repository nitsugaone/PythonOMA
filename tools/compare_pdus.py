#!/usr/bin/env python3
"""
CLI diff tool: compare your generated PDU against a real operator capture.

Usage (two .bin files):
    python tools/compare_pdus.py --gen pdu.bin --ref real_operator.bin

Usage (hex strings):
    python tools/compare_pdus.py \
        --gen-hex 060504... \
        --ref-hex 060504...
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from debug.pdu_diff import compare_pdus, load_pdu_bin, load_pdu_hex
from debug.pdu_debug import debug_pdu


def main():
    parser = argparse.ArgumentParser(description="OMA CP PDU diff tool")
    group_gen = parser.add_mutually_exclusive_group(required=True)
    group_gen.add_argument("--gen",     help="Generated PDU .bin file")
    group_gen.add_argument("--gen-hex", help="Generated PDU as hex string")

    group_ref = parser.add_mutually_exclusive_group(required=True)
    group_ref.add_argument("--ref",     help="Reference PDU .bin file")
    group_ref.add_argument("--ref-hex", help="Reference PDU as hex string")

    args = parser.parse_args()

    gen = load_pdu_bin(args.gen) if args.gen else load_pdu_hex(args.gen_hex)
    ref = load_pdu_bin(args.ref) if args.ref else load_pdu_hex(args.ref_hex)

    debug_pdu(gen, label="GENERATED")
    debug_pdu(ref, label="REFERENCE")
    compare_pdus(gen, ref, label_gen="generated", label_ref="reference")


if __name__ == "__main__":
    main()
