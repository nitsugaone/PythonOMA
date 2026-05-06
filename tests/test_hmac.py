import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from oma.hmac_signer import HMACSigner, SecurityLevel
from core.pdu_builder import PDUBuilder


PAYLOAD = b"\x03\x0B\x6A\x00\x45test"


def test_userpin_mac_is_16_bytes():
    mac = HMACSigner.sign(PAYLOAD, SecurityLevel.USERPIN, pin="1234")
    assert isinstance(mac, bytes)
    assert len(mac) == 16


def test_netwpin_mac_is_16_bytes():
    mac = HMACSigner.sign(PAYLOAD, SecurityLevel.NETWPIN, imsi="722070123456789")
    assert len(mac) == 16


def test_mac_verify_roundtrip():
    mac = HMACSigner.sign(PAYLOAD, SecurityLevel.USERPIN, pin="abcd")
    assert HMACSigner.verify(PAYLOAD, mac, SecurityLevel.USERPIN, pin="abcd")


def test_mac_wrong_pin_fails():
    mac = HMACSigner.sign(PAYLOAD, SecurityLevel.USERPIN, pin="abcd")
    assert not HMACSigner.verify(PAYLOAD, mac, SecurityLevel.USERPIN, pin="wrong")


def test_signed_pdu_longer_than_unsigned():
    unsigned = PDUBuilder.build_full(
        "apn", "", "http://mmsc", "1.1.1.1", 8080
    )
    signed = PDUBuilder.build_full(
        "apn", "", "http://mmsc", "1.1.1.1", 8080,
        security_level=SecurityLevel.USERPIN,
        pin="1234"
    )
    # signed has extra 17 bytes in WSP (0x12 + 16 MAC bytes)
    assert len(signed) > len(unsigned)
    assert len(signed) - len(unsigned) == 17


def test_netwpin_requires_imsi():
    import pytest
    with pytest.raises(ValueError, match="IMSI"):
        HMACSigner.sign(PAYLOAD, SecurityLevel.NETWPIN, imsi="")
