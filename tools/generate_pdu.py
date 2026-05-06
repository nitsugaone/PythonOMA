#!/usr/bin/env python3
"""
CLI tool: generate and inspect a PDU for a given APN profile.

Usage:
    python tools/generate_pdu.py \
        --apn apn1.catel.org.ar \
        --user imowi \
        --mmsc http://mmsc.imowi.ar \
        --proxy 10.10.10.10 \
        --port 8080 \
        --napid internet \
        --out pdu.bin
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.pdu_builder import PDUBuilder
from debug.pdu_debug import debug_pdu, export_pdu


def main():
    parser = argparse.ArgumentParser(description="OMA CP PDU generator")
    parser.add_argument("--apn",   required=True)
    parser.add_argument("--user",  default="")
    parser.add_argument("--mmsc",  required=True)
    parser.add_argument("--proxy", required=True)
    parser.add_argument("--port",  type=int, default=8080)
    parser.add_argument("--napid", default="internet")
    parser.add_argument("--out",   default="pdu.bin",
                        help="Output binary file (default: pdu.bin)")
    args = parser.parse_args()

    pdu = PDUBuilder.build_full(
        apn=args.apn,
        user=args.user,
        mmsc=args.mmsc,
        proxy_ip=args.proxy,
        proxy_port=args.port,
        napid=args.napid,
    )

    debug_pdu(pdu, label=f"APN={args.apn} | PROXY={args.proxy}:{args.port}")
    export_pdu(pdu, args.out)


if __name__ == "__main__":
    main()
