# WSP headers for OMA CP WAP Push

class WSPHeaders:

    @staticmethod
    def build() -> bytes:
        headers = bytes([
            0x2F,  # Content-Type (well-known short)
            0xB6,  # application/vnd.wap.connectivity-wbxml
            0xAF,  # X-WAP-Application-Id
            0x85   # oma-cp
        ])
        return bytes([
            0x01,        # Transaction ID
            0x06,        # PDU Type: Push
            len(headers) # ✅ real header length (not hardcoded)
        ]) + headers
