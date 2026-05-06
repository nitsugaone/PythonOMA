import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from debug.pdu_diff import compare_pdus, load_pdu_hex


def test_identical_pdus():
    pdu = bytes.fromhex("060504" + "0b84" + "23f0" + "0106040b")
    result = compare_pdus(pdu, pdu)
    assert result["equal"] is True
    assert result["diff_count"] == 0


def test_different_pdus():
    a = bytes([0x01, 0x02, 0x03, 0x04])
    b = bytes([0x01, 0xFF, 0x03, 0x04])
    result = compare_pdus(a, b)
    assert result["equal"] is False
    assert result["diff_count"] == 1
    assert result["diffs"][0]["offset"] == 1


def test_length_difference():
    a = bytes([0x01, 0x02, 0x03])
    b = bytes([0x01, 0x02, 0x03, 0x04, 0x05])
    result = compare_pdus(a, b)
    assert result["len_generated"] == 3
    assert result["len_reference"] == 5


def test_load_pdu_hex():
    pdu = load_pdu_hex("06 05 04 0B 84")
    assert pdu == bytes([0x06, 0x05, 0x04, 0x0B, 0x84])
