#!/usr/bin/env python3
"""
CLI tool: generate and inspect a PDU for a given APN profile.

Usage (unsigned):
    python tools/generate_pdu.py \
        --apn apn1.catel.org.ar --user imowi \
        --mmsc http://mmsc.imowi.ar \
        --proxy 10.10.10.10 --port 8080 \
        --napid internet --out pdu.bin

Usage (signed, USERPIN):
    python tools/generate_pdu.py \
        --apn apn1.catel.org.ar --user imowi \
        --mmsc http://mmsc.imowi.ar \
        --proxy 10.10.10.10 --port 8080 \
        --security USERPIN --pin 1234 --out pdu_signed.bin

Usage (signed, NETWPIN):
    python tools/generate_pdu.py ... --security NETWPIN --imsi 722070123456789
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.pdu_builder import PDUBuilder
from oma.hmac_signer import SecurityLevel
from debug.pdu_debug import debug_pdu, export_pdu


def main():
    parser = argparse.ArgumentParser(description="OMA CP PDU generator")
    parser.add_argument("--apn",      required=True)
    parser.add_argument("--user",     default="")
    parser.add_argument("--mmsc",     required=True)
    parser.add_argument("--proxy",    required=True)
    parser.add_argument("--port",     type=int, default=8080)
    parser.add_argument("--napid",    default="internet")
    parser.add_argument("--out",      default="pdu.bin")
    parser.add_argument("--security", choices=[l.value for l in SecurityLevel],
                        default=None, help="HMAC security level (omit = unsigned)")
    parser.add_argument("--pin",      default="", help="PIN for USERPIN/USERNETWPIN")
    parser.add_argument("--imsi",     default="", help="IMSI for NETWPIN/USERNETWPIN")
    args = parser.parse_args()

    sec_level = SecurityLevel(args.security) if args.security else None

    pdu = PDUBuilder.build_full(
        apn=args.apn,
        user=args.user,
        mmsc=args.mmsc,
        proxy_ip=args.proxy,
        proxy_port=args.port,
        napid=args.napid,
        security_level=sec_level,
        imsi=args.imsi,
        pin=args.pin,
    )

    signed_label = f"SIGNED ({args.security})" if sec_level else "UNSIGNED"
    debug_pdu(pdu, label=f"APN={args.apn} | {signed_label}")
    export_pdu(pdu, args.out)


if __name__ == "__main__":
    main()
