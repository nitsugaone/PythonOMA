from oma.wbxml import WBXMLFull
from oma.wap_push import WapPush
from oma.wsp_headers import WSPHeaders
from oma.hmac_signer import HMACSigner, SecurityLevel
from typing import Optional


class PDUBuilder:

    @staticmethod
    def build_full(
        apn: str,
        user: str,
        mmsc: str,
        proxy_ip: str,
        proxy_port: int,
        napid: str = "internet",
        # HMAC signing (optional — set level + credentials for signed PDU)
        security_level: Optional[SecurityLevel] = None,
        imsi: str = "",
        pin: str = "",
    ) -> bytes:
        wbxml = WBXMLFull.encode_full_profile(
            apn, user, mmsc, proxy_ip, proxy_port, napid
        )

        mac = None
        if security_level is not None:
            mac = HMACSigner.sign(wbxml, level=security_level, imsi=imsi, pin=pin)

        wsp = WSPHeaders.build(mac=mac)
        return WapPush.build_push(wsp + wbxml)
