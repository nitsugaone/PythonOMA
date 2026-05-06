# PDU debug tool — inspect any generated PDU before sending to device

def debug_pdu(pdu: bytes, label: str = "") -> None:
    if label:
        print(f"\n{'='*50}")
        print(f"  {label}")
        print(f"{'='*50}")

    print(f"TOTAL LEN : {len(pdu)} bytes")
    print(f"FULL HEX  : {pdu.hex()}")
    print()

    # --- UDH (bytes 0-6) ---
    udh = pdu[:7]
    print(f"[UDH]     : {udh.hex()}")
    print(f"  UDH len   : 0x{pdu[0]:02X} ({pdu[0]})")
    print(f"  IEI       : 0x{pdu[1]:02X} 0x{pdu[2]:02X}")
    dest_port = (pdu[3] << 8) | pdu[4]
    src_port  = (pdu[5] << 8) | pdu[6]
    print(f"  Dest port : {dest_port} (0x{dest_port:04X}) {'\u2705 WAP Push' if dest_port == 2948 else '\u26a0\ufe0f NOT 2948'}")
    print(f"  Src  port : {src_port}  (0x{src_port:04X})")
    print()

    # --- WSP (bytes 7-10) ---
    wsp = pdu[7:11]
    print(f"[WSP]     : {wsp.hex()}")
    print(f"  TID       : 0x{pdu[7]:02X}")
    pdu_type = pdu[8]
    print(f"  PDU type  : 0x{pdu_type:02X} {'\u2705 Push' if pdu_type == 0x06 else '\u26a0\ufe0f unexpected'}")
    hdr_len   = pdu[9]
    print(f"  Hdr len   : {hdr_len} bytes")
    ct_byte   = pdu[10] if len(pdu) > 10 else None
    if ct_byte is not None:
        ct_ok = ct_byte in (0x2F, 0xB6)
        print(f"  Content-T : 0x{ct_byte:02X} {'\u2705 OMA CP' if ct_ok else '\u26a0\ufe0f check content-type'}")
    print()

    # --- WBXML header (first 4 bytes after WSP) ---
    wbxml_start = 7 + 3 + hdr_len  # UDH + TID+type+hdrlen + headers
    wbxml = pdu[wbxml_start:wbxml_start + 5]
    if len(wbxml) >= 3:
        print(f"[WBXML]   : {wbxml.hex()}")
        print(f"  Version   : 0x{wbxml[0]:02X} {'\u2705 1.3' if wbxml[0] == 0x03 else '\u26a0\ufe0f not 1.3'}")
        pub_id = wbxml[1]
        print(f"  Public ID : 0x{pub_id:02X} {'\u2705 OMA CP' if pub_id == 0x0B else '\u26a0\ufe0f not OMA CP (0x0B)'}")
        charset = wbxml[2]
        print(f"  Charset   : 0x{charset:02X} {'\u2705 UTF-8' if charset == 0x6A else '\u26a0\ufe0f not UTF-8'}")
    print()


def export_pdu(pdu: bytes, filename: str = "pdu.bin") -> None:
    with open(filename, "wb") as f:
        f.write(pdu)
    print(f"\u2705 PDU saved to {filename} ({len(pdu)} bytes)")
    print(f"   hex: {pdu.hex()}")
