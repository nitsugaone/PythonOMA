# WBXML encoder for OMA CP (Client Provisioning)
# Single source of truth — replaces wbxml_encoder.py, wbxml_real.py, wbxml_full.py

class WBXMLFull:

    VERSION = 0x03
    PUBLIC_ID = 0x0B  # OMA CP
    CHARSET = 0x6A    # UTF-8

    TAGS = {
        "wap-provisioningdoc": 0x05,
        "characteristic": 0x06,
        "parm": 0x07
    }

    END = 0x01
    STR_I = 0x03

    @staticmethod
    def _str(s: str) -> bytes:
        return bytes([WBXMLFull.STR_I]) + s.encode() + b"\x00"

    @staticmethod
    def _parm(name: str, value: str) -> bytes:
        out = bytearray()
        out.append(WBXMLFull.TAGS["parm"] | 0xC0)
        out.extend(WBXMLFull._str(name))
        out.extend(WBXMLFull._str(value))
        out.append(WBXMLFull.END)
        return bytes(out)

    @staticmethod
    def _characteristic(type_name: str, parms: bytes) -> bytes:
        out = bytearray()
        out.append(WBXMLFull.TAGS["characteristic"] | 0xC0)
        out.extend(WBXMLFull._str(type_name))
        out.extend(parms)
        out.append(WBXMLFull.END)
        return bytes(out)

    @staticmethod
    def encode_full_profile(
        apn: str,
        user: str,
        mmsc: str,
        proxy_ip: str,
        proxy_port: int
    ) -> bytes:
        out = bytearray()

        # WBXML header
        out.extend([
            WBXMLFull.VERSION,
            WBXMLFull.PUBLIC_ID,
            WBXMLFull.CHARSET,
            0x00  # string table length
        ])

        # <wap-provisioningdoc> (has children + attributes)
        out.append(WBXMLFull.TAGS["wap-provisioningdoc"] | 0x40)

        # NAPDEF: APN + auth
        napdef_parms = (
            WBXMLFull._parm("NAPID", apn) +
            WBXMLFull._parm("BEARER", "GSM-GPRS") +
            WBXMLFull._parm("NAME", apn) +
            WBXMLFull._parm("NAP-ADDRESS", apn) +
            WBXMLFull._parm("NAP-ADDRTYPE", "APN") +
            WBXMLFull._characteristic(
                "NAPAUTHINFO",
                WBXMLFull._parm("AUTHTYPE", "PAP") +
                WBXMLFull._parm("AUTHNAME", user) +
                WBXMLFull._parm("AUTHSECRET", "")
            )
        )
        out.extend(WBXMLFull._characteristic("NAPDEF", napdef_parms))

        # PXLOGICAL: MMS proxy
        px_parms = (
            WBXMLFull._parm("PROXY-ID", proxy_ip) +
            WBXMLFull._parm("NAME", "MMS Proxy") +
            WBXMLFull._parm("STARTPAGE", mmsc) +
            WBXMLFull._characteristic(
                "PXAUTHINFO",
                WBXMLFull._parm("PXAUTH-TYPE", "HTTP-BASIC") +
                WBXMLFull._parm("PXAUTH-ID", "") +
                WBXMLFull._parm("PXAUTH-PW", "")
            ) +
            WBXMLFull._characteristic(
                "PORT",
                WBXMLFull._parm("PORTNBR", str(proxy_port)) +
                WBXMLFull._parm("SERVICE", "CO-WSP")
            )
        )
        out.extend(WBXMLFull._characteristic("PXLOGICAL", px_parms))

        # APPLICATION: MMS settings
        app_parms = (
            WBXMLFull._parm("APPID", "w4") +
            WBXMLFull._parm("NAME", "MMS") +
            WBXMLFull._parm("ADDR", mmsc) +
            WBXMLFull._characteristic(
                "RESOURCE",
                WBXMLFull._parm("URI", mmsc) +
                WBXMLFull._parm("NAME", "MMS")
            )
        )
        out.extend(WBXMLFull._characteristic("APPLICATION", app_parms))

        # end root
        out.append(WBXMLFull.END)

        return bytes(out)
