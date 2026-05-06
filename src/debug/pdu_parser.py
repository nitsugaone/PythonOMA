# OMA CP PDU parser — reverse direction
# Input:  raw PDU bytes (from AT+CMGR capture or SMS app export)
# Output: structured dict with UDH, WSP, WBXML layers decoded
#
# Usage:
#   from debug.pdu_parser import parse_pdu
#   result = parse_pdu(bytes.fromhex("060504..."))

from typing import Optional


SEC_LEVELS = {
    "NETWPIN":     0,
    "USERPIN":     1,
    "USERNETWPIN": 2,
    "USERPINMAC":  3,
}

WSP_CONTENT_TYPES = {
    0x2F: "application/vnd.wap.connectivity-wbxml (short)",
    0xB6: "application/vnd.wap.connectivity-wbxml",
    0x03: "application/vnd.wap.multipart.related",
}

WSP_APP_IDS = {
    0x85: "oma-cp",
    0x86: "oma-drm",
}

WBXML_PUBLIC_IDS = {
    0x01: "UNKNOWN",
    0x0B: "OMA CP (WAP provisioning 1.0)",
    0x24: "OMA CP (WAP provisioning 1.1)",
}

OMA_TAGS = {
    0x05: "wap-provisioningdoc",
    0x06: "characteristic",
    0x07: "parm",
}


class ParseError(Exception):
    pass


def _read_str_i(data: bytes, pos: int) -> tuple[str, int]:
    """Read STR_I inline string (0x03 + null-terminated UTF-8)."""
    if data[pos] != 0x03:
        raise ParseError(f"Expected STR_I (0x03) at offset {pos}, got 0x{data[pos]:02X}")
    pos += 1
    end = data.index(0x00, pos)
    text = data[pos:end].decode("utf-8", errors="replace")
    return text, end + 1


def _parse_wbxml_body(data: bytes, pos: int, depth: int = 0) -> tuple[list, int]:
    """Recursively parse WBXML elements after the 4-byte header."""
    nodes = []
    while pos < len(data):
        byte = data[pos]

        if byte == 0x01:  # END
            return nodes, pos + 1

        tag_id  = byte & 0x3F
        has_content  = bool(byte & 0x40)
        has_attrs    = bool(byte & 0x80)
        tag_name = OMA_TAGS.get(tag_id, f"UNKNOWN_TAG(0x{tag_id:02X})")
        pos += 1

        node = {"tag": tag_name, "attrs": [], "children": []}

        # attributes: STR_I pairs until END
        if has_attrs:
            while pos < len(data) and data[pos] != 0x01:
                try:
                    name,  pos = _read_str_i(data, pos)
                    value, pos = _read_str_i(data, pos)
                    node["attrs"].append({"name": name, "value": value})
                except (ParseError, ValueError):
                    break
            if pos < len(data) and data[pos] == 0x01:
                pos += 1  # END of attrs

        # children
        if has_content:
            children, pos = _parse_wbxml_body(data, pos, depth + 1)
            node["children"] = children

        nodes.append(node)
    return nodes, pos


def parse_pdu(pdu: bytes) -> dict:
    """
    Parse a raw OMA CP WAP Push PDU into structured layers.
    Returns a dict with keys: udh, wsp, wbxml, errors.
    """
    result = {"raw_hex": pdu.hex(), "raw_len": len(pdu),
              "udh": {}, "wsp": {}, "wbxml": {}, "errors": []}
    pos = 0

    # ------------------------------------------------------------------ UDH
    try:
        udh_len = pdu[pos];  pos += 1
        iei     = pdu[pos];  pos += 1
        iei_len = pdu[pos];  pos += 1
        dest_port = (pdu[pos] << 8) | pdu[pos + 1];  pos += 2
        src_port  = (pdu[pos] << 8) | pdu[pos + 1];  pos += 2
        result["udh"] = {
            "length":    udh_len,
            "iei":       f"0x{iei:02X}",
            "dest_port": dest_port,
            "src_port":  src_port,
            "wap_push":  dest_port == 2948,
        }
        if dest_port != 2948:
            result["errors"].append(
                f"Dest port is {dest_port}, expected 2948 (WAP Push)")
    except IndexError:
        result["errors"].append("PDU too short to parse UDH")
        return result

    # ------------------------------------------------------------------ WSP
    try:
        tid      = pdu[pos];  pos += 1
        pdu_type = pdu[pos];  pos += 1
        hdr_len  = pdu[pos];  pos += 1
        hdr_end  = pos + hdr_len

        wsp = {
            "transaction_id": f"0x{tid:02X}",
            "pdu_type":       f"0x{pdu_type:02X}",
            "pdu_type_name":  "Push" if pdu_type == 0x06 else "UNKNOWN",
            "header_length":  hdr_len,
            "content_type":   None,
            "app_id":         None,
            "mac":            None,
            "extra_headers":  [],
        }

        # parse WSP headers
        hpos = pos
        while hpos < hdr_end:
            hbyte = pdu[hpos];  hpos += 1
            if hbyte == 0x2F:   # CT short + next byte
                ct_val = pdu[hpos]; hpos += 1
                wsp["content_type"] = WSP_CONTENT_TYPES.get(
                    ct_val, f"0x{ct_val:02X}")
            elif hbyte == 0xAF:  # App-Id
                app_val = pdu[hpos]; hpos += 1
                wsp["app_id"] = WSP_APP_IDS.get(app_val, f"0x{app_val:02X}")
            elif hbyte == 0x12:  # X-WAP-Connectivity-MAC
                mac_bytes = pdu[hpos:hpos + 16]; hpos += 16
                wsp["mac"] = mac_bytes.hex()
            else:
                wsp["extra_headers"].append(f"0x{hbyte:02X}")

        result["wsp"] = wsp
        pos = hdr_end

        if pdu_type != 0x06:
            result["errors"].append(
                f"PDU type 0x{pdu_type:02X} is not Push (0x06)")
    except IndexError:
        result["errors"].append("PDU too short to parse WSP")
        return result

    # --------------------------------------------------------------- WBXML
    try:
        wbxml_raw = pdu[pos:]
        version   = wbxml_raw[0]
        pub_id    = wbxml_raw[1]
        charset   = wbxml_raw[2]
        # strtbl_len can be multi-byte but almost always 0x00 for OMA CP
        strtbl    = wbxml_raw[3]

        wbxml_info = {
            "version":    f"0x{version:02X}",
            "version_ok": version == 0x03,
            "public_id":  f"0x{pub_id:02X}",
            "public_id_name": WBXML_PUBLIC_IDS.get(pub_id, "UNKNOWN"),
            "oma_cp_ok":  pub_id == 0x0B,
            "charset":    f"0x{charset:02X}",
            "utf8_ok":    charset == 0x6A,
            "body_offset": pos + 4,
            "body_hex":   wbxml_raw[4:].hex(),
            "elements":   [],
        }

        # parse body
        try:
            elements, _ = _parse_wbxml_body(wbxml_raw, 4)
            wbxml_info["elements"] = elements
        except Exception as e:
            result["errors"].append(f"WBXML body parse error: {e}")

        result["wbxml"] = wbxml_info

        if not wbxml_info["version_ok"]:
            result["errors"].append(
                f"WBXML version 0x{version:02X} != 0x03")
        if not wbxml_info["oma_cp_ok"]:
            result["errors"].append(
                f"Public ID 0x{pub_id:02X} is not OMA CP (0x0B)")

    except IndexError:
        result["errors"].append("PDU too short to parse WBXML header")

    return result


def print_parsed(parsed: dict, indent: int = 2) -> None:
    """Pretty-print a parsed PDU dict."""
    pad = " " * indent

    print(f"\n{'='*60}")
    print(f"  RAW  {parsed['raw_len']} bytes  {parsed['raw_hex'][:40]}...")
    print(f"{'='*60}")

    udh = parsed.get("udh", {})
    print(f"\n[UDH]")
    print(f"{pad}dest_port : {udh.get('dest_port')} "
          f"{'\u2705 WAP Push' if udh.get('wap_push') else '\u26a0\ufe0f NOT 2948'}")
    print(f"{pad}src_port  : {udh.get('src_port')}")

    wsp = parsed.get("wsp", {})
    print(f"\n[WSP]")
    print(f"{pad}pdu_type  : {wsp.get('pdu_type_name')}")
    print(f"{pad}hdr_len   : {wsp.get('header_length')}")
    print(f"{pad}content-t : {wsp.get('content_type')}")
    print(f"{pad}app_id    : {wsp.get('app_id')}")
    mac = wsp.get("mac")
    print(f"{pad}MAC       : {mac if mac else 'none (unsigned)'}")
    if wsp.get("extra_headers"):
        print(f"{pad}extra hdrs: {wsp['extra_headers']}")

    wx = parsed.get("wbxml", {})
    print(f"\n[WBXML]")
    print(f"{pad}version   : {wx.get('version')} "
          f"{'\u2705' if wx.get('version_ok') else '\u26a0\ufe0f'}")
    print(f"{pad}public_id : {wx.get('public_id')} {wx.get('public_id_name')} "
          f"{'\u2705' if wx.get('oma_cp_ok') else '\u26a0\ufe0f'}")
    print(f"{pad}charset   : {wx.get('charset')} "
          f"{'\u2705 UTF-8' if wx.get('utf8_ok') else '\u26a0\ufe0f'}")

    def _print_elements(elements, depth=0):
        for el in elements:
            prefix = "  " * depth
            attrs = ", ".join(
                f"{a['name']}={a['value']!r}" for a in el.get("attrs", [])
            )
            print(f"{pad}{prefix}<{el['tag']}{(' ' + attrs) if attrs else ''}>")
            _print_elements(el.get("children", []), depth + 1)

    print(f"{pad}elements:")
    _print_elements(wx.get("elements", []))

    errors = parsed.get("errors", [])
    if errors:
        print(f"\n\u26a0\ufe0f  Errors / warnings:")
        for e in errors:
            print(f"{pad}{e}")
    else:
        print(f"\n\u2705 No errors detected")
