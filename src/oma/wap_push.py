# Build WAP PUSH PDU — UDH + WSP + WBXML payload

class WapPush:

    @staticmethod
    def build_push(wsp_and_payload: bytes) -> bytes:
        udh = bytes([
            0x06,        # UDH length
            0x05, 0x04,  # IEI: application port addressing (16-bit)
            0x0B, 0x84,  # Destination port: 2948 (WAP Push)
            0x23, 0xF0   # Source port
        ])
        return udh + wsp_and_payload
