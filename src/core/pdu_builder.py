from oma.wbxml_encoder import WBXMLEncoder
from oma.wap_push import WapPush

class PDUBuilder:

    @staticmethod
    def build(xml_payload: bytes) -> bytes:
        wbxml = WBXMLEncoder.encode(xml_payload)
        wap_push = WapPush.build_push(wbxml)
        return wap_push
