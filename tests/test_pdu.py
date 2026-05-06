import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.pdu_builder import PDUBuilder


def test_pdu_generation():
    pdu = PDUBuilder.build_full(
        apn="apn.test",
        user="user",
        mmsc="http://mmsc.test",
        proxy_ip="1.1.1.1",
        proxy_port=8080
    )
    assert isinstance(pdu, bytes)
    assert len(pdu) > 10


def test_pdu_starts_with_udh():
    pdu = PDUBuilder.build_full(
        apn="internet",
        user="",
        mmsc="http://mmsc.example.com",
        proxy_ip="192.168.0.1",
        proxy_port=8080
    )
    # UDH starts with 0x06 (length)
    assert pdu[0] == 0x06
    # Destination port bytes: 0x0B 0x84 = 2948
    assert pdu[3] == 0x0B
    assert pdu[4] == 0x84


def test_wbxml_header():
    from oma.wbxml import WBXMLFull
    payload = WBXMLFull.encode_full_profile(
        "apn.test", "user", "http://mmsc", "10.0.0.1", 8080
    )
    # WBXML version 1.3
    assert payload[0] == 0x03
    # Public ID: OMA CP
    assert payload[1] == 0x0B
    # Charset: UTF-8
    assert payload[2] == 0x6A
