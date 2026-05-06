# Testing matrix logger — record per-device results during real device testing
# Saves results to matrix.csv for tracking across sessions

import csv
import os
from datetime import datetime
from typing import Optional

MATRIX_FILE = "matrix.csv"

FIELDS = [
    "timestamp", "device", "brand", "android_version",
    "pdu_version", "receives_sms", "shows_popup",
    "installs_apn", "mms_works", "notes"
]


def log_result(
    device: str,
    brand: str,
    android_version: str,
    pdu_version: str,
    receives_sms: bool,
    shows_popup: bool,
    installs_apn: bool,
    mms_works: bool,
    notes: str = ""
) -> None:
    exists = os.path.exists(MATRIX_FILE)
    with open(MATRIX_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":       datetime.utcnow().isoformat(),
            "device":          device,
            "brand":           brand,
            "android_version": android_version,
            "pdu_version":     pdu_version,
            "receives_sms":    receives_sms,
            "shows_popup":     shows_popup,
            "installs_apn":    installs_apn,
            "mms_works":       mms_works,
            "notes":           notes
        })
    print(f"\u2705 Logged: {device} / pdu={pdu_version} / "
          f"sms={receives_sms} popup={shows_popup} "
          f"apn={installs_apn} mms={mms_works}")


def print_matrix() -> None:
    if not os.path.exists(MATRIX_FILE):
        print("No matrix.csv found. Run some tests first.")
        return
    with open(MATRIX_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("Matrix is empty.")
        return
    col_w = [16, 10, 8, 10, 6, 6, 5, 5]
    headers = ["device", "brand", "android", "pdu_ver",
               "sms", "popup", "apn", "mms"]
    fmt = "".join(f"{{:<{w}}}" for w in col_w)
    print(fmt.format(*headers))
    print("-" * sum(col_w))
    for r in rows:
        print(fmt.format(
            r["device"][:15], r["brand"][:9], r["android_version"][:7],
            r["pdu_version"][:9],
            r["receives_sms"], r["shows_popup"],
            r["installs_apn"], r["mms_works"]
        ))
