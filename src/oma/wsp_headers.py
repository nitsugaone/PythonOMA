# WSP headers for OMA CP WAP Push
# Supports optional HMAC-MD5 MAC header (level operador)

from typing import Optional


class WSPHeaders:

    # Content-Type: application/vnd.wap.connectivity-wbxml
    CT_OMA_CP = bytes([0x2F, 0xB6])

    # X-WAP-Application-Id: oma-cp
    APP_ID    = bytes([0xAF, 0x85])

    @staticmethod
    def build(mac: Optional[bytes] = None) -> bytes:
        """
        Build WSP headers.
        If mac (16-byte HMAC-MD5) is provided, embeds X-WAP-Connectivity-MAC.
        """
        headers = bytearray(WSPHeaders.CT_OMA_CP + WSPHeaders.APP_ID)

        if mac is not None:
            if len(mac) != 16:
                raise ValueError("MAC must be 16 bytes (HMAC-MD5)")
            # X-WAP-Connectivity-MAC: header code 0x12 + 16 MAC bytes
            headers.append(0x12)
            headers.extend(mac)

        return bytes([
            0x01,          # Transaction ID
            0x06,          # PDU Type: Push
            len(headers)   # ✅ real header length
        ]) + bytes(headers)
