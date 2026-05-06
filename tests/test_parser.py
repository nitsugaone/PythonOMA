import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from debug.pdu_parser import parse_pdu
from core.pdu_builder import PDUBuilder


def _build():
    return PDUBuilder.build_full(
        apn="internet", user="",
        mmsc="http://mmsc.test",
        proxy_ip="10.0.0.1", proxy_port=8080
    )


def test_parse_udh():
    pdu = _build()
    result = parse_pdu(pdu)
    assert result["udh"]["dest_port"] == 2948
    assert result["udh"]["wap_push"] is True


def test_parse_wsp():
    pdu = _build()
    result = parse_pdu(pdu)
    assert result["wsp"]["pdu_type_name"] == "Push"
    assert result["wsp"]["header_length"] == 4
    assert result["wsp"]["mac"] is None  # unsigned


def test_parse_wbxml_header():
    pdu = _build()
    result = parse_pdu(pdu)
    assert result["wbxml"]["version_ok"] is True
    assert result["wbxml"]["oma_cp_ok"] is True
    assert result["wbxml"]["utf8_ok"] is True


def test_parse_wbxml_contains_napdef():
    pdu = _build()
    result = parse_pdu(pdu)

    def find_tag(elements, tag):
        for el in elements:
            if el["tag"] == tag:
                return True
            if find_tag(el.get("children", []), tag):
                return True
        return False

    assert find_tag(result["wbxml"]["elements"], "characteristic")


def test_parse_no_errors_on_valid_pdu():
    pdu = _build()
    result = parse_pdu(pdu)
    assert result["errors"] == []


def test_parse_signed_pdu_has_mac():
    from oma.hmac_signer import SecurityLevel
    pdu = PDUBuilder.build_full(
        apn="internet", user="",
        mmsc="http://mmsc.test",
        proxy_ip="10.0.0.1", proxy_port=8080,
        security_level=SecurityLevel.USERPIN,
        pin="1234"
    )
    result = parse_pdu(pdu)
    assert result["wsp"]["mac"] is not None
    assert len(result["wsp"]["mac"]) == 32  # 16 bytes hex = 32 chars


def test_parse_corrupt_pdu_has_errors():
    result = parse_pdu(b"\x01\x02")
    assert len(result["errors"]) > 0
