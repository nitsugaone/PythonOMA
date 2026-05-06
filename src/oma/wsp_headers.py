# Proper WSP header builder for OMA CP Push

class WSPHeaders:

    @staticmethod
    def build():
        return bytes([
            0x01,  # Transaction ID
            0x06,  # Push PDU
            0x2E,  # Headers length (approx)

            # Content-Type: application/vnd.wap.connectivity-wbxml
            0x2F,  # well-known media
            0xB6,  # wbxml connectivity

            # X-WAP-Application-Id: x-wap-application:oma-cp
            0xAF,
            0x85
        ])
