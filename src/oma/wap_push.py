# Build WAP PUSH PDU (simplified but structurally correct)

class WapPush:

    @staticmethod
    def build_push(wbxml_payload: bytes) -> bytes:
        # UDH for WAP Push
        udh = bytes([
            0x06,        # UDH length
            0x05, 0x04,  # IEI + length
            0x0B, 0x84,  # Port 2948 (dest)
            0x23, 0xF0   # Source port (arbitrary)
        ])

        # WSP headers
        headers = bytes([
            0x01,  # Transaction ID
            0x06,  # PDU Type: Push
            0x04,  # Headers length
            0x0B,  # Content-Type: application/vnd.wap.connectivity-wbxml
        ])

        return udh + headers + wbxml_payload
