# WBXML encoder closer to OMA CP spec (token-based minimal subset)

class WBXMLReal:

    TAG_MAP = {
        "wap-provisioningdoc": 0x05,
        "characteristic": 0x06,
        "parm": 0x07
    }

    ATTR_MAP = {
        "type": 0x05,
        "name": 0x06,
        "value": 0x07
    }

    @staticmethod
    def encode(xml_dict):
        # ⚠️ This is still partial but token-based (better than raw XML)
        header = bytes([
            0x03,  # WBXML 1.3
            0x0B,  # Public ID (OMA CP)
            0x6A,  # UTF-8
            0x00
        ])

        body = bytearray()

        def encode_element(tag, attrs):
            body.append(WBXMLReal.TAG_MAP.get(tag, 0x05))
            for k, v in attrs.items():
                body.append(WBXMLReal.ATTR_MAP.get(k, 0x05))
                body.extend(v.encode() + b'\x00')

        # minimal structure
        encode_element("wap-provisioningdoc", {})

        return header + bytes(body)
