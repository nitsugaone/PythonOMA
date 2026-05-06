# PDU comparator — diff your generated PDU against a real operator capture
# Usage: compare_pdus(your_pdu, reference_pdu)

from typing import Optional


def compare_pdus(
    generated: bytes,
    reference: bytes,
    label_gen: str = "generated",
    label_ref: str = "reference",
    context_bytes: int = 2
) -> dict:
    """
    Byte-level diff between two PDUs.
    Returns a report dict and prints a human-readable summary.
    """
    diffs = []
    max_len = max(len(generated), len(reference))

    for i in range(max_len):
        gen_byte = generated[i] if i < len(generated) else None
        ref_byte = reference[i] if i < len(reference) else None
        if gen_byte != ref_byte:
            # grab surrounding context from reference
            ctx_start = max(0, i - context_bytes)
            ctx_end   = min(len(reference), i + context_bytes + 1)
            diffs.append({
                "offset":  i,
                "generated": f"0x{gen_byte:02X}" if gen_byte is not None else "MISSING",
                "reference": f"0x{ref_byte:02X}" if ref_byte is not None else "EXTRA",
                "context":   reference[ctx_start:ctx_end].hex()
            })

    # --- print report ---
    print(f"\n{'='*56}")
    print(f"  PDU DIFF: {label_gen}  vs  {label_ref}")
    print(f"{'='*56}")
    print(f"  {label_gen:<20} {len(generated):>4} bytes   {generated.hex()[:32]}...")
    print(f"  {label_ref:<20} {len(reference):>4} bytes   {reference.hex()[:32]}...")
    print(f"  Length delta: {len(generated) - len(reference):+d} bytes")
    print()

    if not diffs:
        print("  \u2705 PDUs are IDENTICAL")
    else:
        print(f"  \u26a0\ufe0f  {len(diffs)} difference(s) found:\n")
        for d in diffs[:30]:  # cap output at 30 diffs
            print(
                f"  offset {d['offset']:>4} (0x{d['offset']:04X})  "
                f"{label_gen}: {d['generated']:<8}  "
                f"{label_ref}: {d['reference']:<8}  "
                f"ctx: {d['context']}"
            )
        if len(diffs) > 30:
            print(f"  ... and {len(diffs) - 30} more differences.")

    print()
    return {
        "equal":        len(diffs) == 0,
        "diff_count":   len(diffs),
        "len_generated": len(generated),
        "len_reference": len(reference),
        "diffs":         diffs
    }


def load_pdu_bin(path: str) -> bytes:
    """Load a raw PDU binary file."""
    with open(path, "rb") as f:
        return f.read()


def load_pdu_hex(hex_string: str) -> bytes:
    """Parse a hex string (spaces optional) into bytes."""
    return bytes.fromhex(hex_string.replace(" ", "").strip())
