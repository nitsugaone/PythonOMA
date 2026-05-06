# OMA CP HMAC-MD5 signer (Opción B — nivel operador)
# Spec: OMA-WAP-ProvCont-v1_1 section 11
#
# The HMAC covers the WBXML payload.
# The key is derived from: PIN | IMSI | MSISDN depending on security level.
#
# Security levels:
#   NETWPIN   — key = IMSI  (network-side, no user interaction)
#   USERPIN   — key = PIN   (user must enter PIN on device)
#   USERNETWPIN — key = PIN + IMSI
#   USERPINMAC  — key = PIN  (same as USERPIN, different trust chain)

import hmac
import hashlib
from enum import Enum


class SecurityLevel(str, Enum):
    NETWPIN     = "NETWPIN"
    USERPIN     = "USERPIN"
    USERNETWPIN = "USERNETWPIN"
    USERPINMAC  = "USERPINMAC"


class HMACSigner:

    @staticmethod
    def _derive_key(level: SecurityLevel, imsi: str = "", pin: str = "") -> bytes:
        if level == SecurityLevel.NETWPIN:
            if not imsi:
                raise ValueError("NETWPIN requires IMSI")
            return imsi.encode("ascii")

        elif level == SecurityLevel.USERPIN:
            if not pin:
                raise ValueError("USERPIN requires PIN")
            return pin.encode("ascii")

        elif level == SecurityLevel.USERNETWPIN:
            if not pin or not imsi:
                raise ValueError("USERNETWPIN requires both PIN and IMSI")
            return (pin + imsi).encode("ascii")

        elif level == SecurityLevel.USERPINMAC:
            if not pin:
                raise ValueError("USERPINMAC requires PIN")
            return pin.encode("ascii")

        raise ValueError(f"Unknown security level: {level}")

    @staticmethod
    def sign(
        wbxml_payload: bytes,
        level: SecurityLevel = SecurityLevel.USERPIN,
        imsi: str = "",
        pin: str = ""
    ) -> bytes:
        """
        Returns the HMAC-MD5 MAC (16 bytes) over the WBXML payload.
        Must be embedded into the WSP headers as X-WAP-Connectivity-MAC.
        """
        key = HMACSigner._derive_key(level, imsi, pin)
        mac = hmac.new(key, wbxml_payload, hashlib.md5).digest()
        return mac

    @staticmethod
    def verify(
        wbxml_payload: bytes,
        mac: bytes,
        level: SecurityLevel = SecurityLevel.USERPIN,
        imsi: str = "",
        pin: str = ""
    ) -> bool:
        expected = HMACSigner.sign(wbxml_payload, level, imsi, pin)
        return hmac.compare_digest(expected, mac)
