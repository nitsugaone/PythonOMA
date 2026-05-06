import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.pdu_builder import PDUBuilder
from oma.wbxml import WBXMLFull


def _build(**kwargs):
    defaults = dict(
        apn="apn.test",
        user="user",
        mmsc="http://mmsc.test",
        proxy_ip="1.1.1.1",
        proxy_port=8080,
    )
    defaults.update(kwargs)
    return PDUBuilder.build_full(**defaults)


def test_pdu_is_bytes_and_not_empty():
    pdu = _build()
    assert isinstance(pdu, bytes)
    assert len(pdu) > 20


def test_udh_structure():
    pdu = _build()
    assert pdu[0] == 0x06              # UDH length
    assert pdu[1] == 0x05              # IEI: app port addressing
    assert pdu[2] == 0x04              # IEI length
    dest_port = (pdu[3] << 8) | pdu[4]
    assert dest_port == 2948           # WAP Push port


def test_wsp_push_type():
    pdu = _build()
    # WSP starts at byte 7 (after 7-byte UDH)
    assert pdu[8] == 0x06              # PDU type: Push


def test_wsp_header_length_is_correct():
    pdu = _build()
    declared_hdr_len = pdu[9]
    # Content-Type (0x2F, 0xB6) + App-Id (0xAF, 0x85) = 4 bytes
    assert declared_hdr_len == 4


def test_wbxml_header():
    wbxml = WBXMLFull.encode_full_profile(
        "apn.test", "user", "http://mmsc", "10.0.0.1", 8080
    )
    assert wbxml[0] == 0x03   # WBXML version 1.3
    assert wbxml[1] == 0x0B   # OMA CP public ID
    assert wbxml[2] == 0x6A   # UTF-8


def test_napid_linking_present():
    """TO-NAPID must appear in the WBXML payload for MMS linking to work."""
    wbxml = WBXMLFull.encode_full_profile(
        "internet", "", "http://mmsc.test", "10.0.0.1", 8080, napid="internet"
    )
    assert b"TO-NAPID" in wbxml
    assert b"internet" in wbxml


def test_custom_napid():
    wbxml = WBXMLFull.encode_full_profile(
        "miwifi.ar", "admin", "http://mmsc.ar", "192.168.1.1", 8080,
        napid="miwifi"
    )
    assert b"miwifi" in wbxml
    assert b"TO-NAPID" in wbxml
