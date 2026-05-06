from oma.wbxml import WBXMLFull
from oma.wap_push import WapPush
from oma.wsp_headers import WSPHeaders


class PDUBuilder:

    @staticmethod
    def build_full(
        apn: str,
        user: str,
        mmsc: str,
        proxy_ip: str,
        proxy_port: int,
        napid: str = "internet"
    ) -> bytes:
        wbxml = WBXMLFull.encode_full_profile(
            apn, user, mmsc, proxy_ip, proxy_port, napid
        )
        wsp = WSPHeaders.build()
        return WapPush.build_push(wsp + wbxml)
