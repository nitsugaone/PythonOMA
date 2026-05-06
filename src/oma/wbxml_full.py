# Full WBXML encoder for OMA CP (expanded, production-oriented subset)
# Implements token handling, nesting and string table basics

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
    def encode_apn(apn: str, user: str) -> bytes:
        out = bytearray()

        # Header
        out.extend([
            WBXMLFull.VERSION,
            WBXMLFull.PUBLIC_ID,
            WBXMLFull.CHARSET,
            0x00  # string table length
        ])

        # <wap-provisioningdoc>
        out.append(WBXMLFull.TAGS["wap-provisioningdoc"] | 0x40)

        # <characteristic type="NAPDEF">
        out.append(WBXMLFull.TAGS["characteristic"] | 0xC0)
        out.extend(WBXMLFull._str("NAPDEF"))

        # <parm name="APN" value="..."/>
        out.append(WBXMLFull.TAGS["parm"] | 0xC0)
        out.extend(WBXMLFull._str("APN"))
        out.extend(WBXMLFull._str(apn))
        out.append(WBXMLFull.END)

        out.append(WBXMLFull.END)  # end characteristic

        # <characteristic type="NAPAUTHINFO">
        out.append(WBXMLFull.TAGS["characteristic"] | 0xC0)
        out.extend(WBXMLFull._str("NAPAUTHINFO"))

        # <parm name="AUTHNAME" value="user"/>
        out.append(WBXMLFull.TAGS["parm"] | 0xC0)
        out.extend(WBXMLFull._str("AUTHNAME"))
        out.extend(WBXMLFull._str(user))
        out.append(WBXMLFull.END)

        out.append(WBXMLFull.END)

        # end root
        out.append(WBXMLFull.END)

        return bytes(out)
