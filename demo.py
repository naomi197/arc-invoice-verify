"""Offline fixture demo; it never calls RPC and is always marked NOT VERIFIED."""
from __future__ import annotations

import argparse

def build_fixture():
    """Build an explicitly unverified fixture without starting Streamlit."""
    from src.models import Invoice, VerificationResult
    from src.arc_verify_core.evidence import snapshot_hash, utc_now
    from src.receipt_generator import AuditReceiptGenerator

    invoice = Invoice(
        invoice_id="DEMO-001", description="Offline fixture",
        recipient_address="0x" + "1" * 40, payer_address="0x" + "2" * 40,
        amount_expected_usdc="1.00",
    )
    body = {
        "snapshot_version": "arc-invoice-verify/3",
        "invoice": invoice.model_dump(mode="json"),
        "tx_hash": "0x" + "a" * 64, "verified": False,
        "outcome": "unsupported", "reason": "DEMO ONLY: no network call.",
        "policy": {"fixture": True}, "evidence": {"fixture_only": True},
        "chain_id": 5042002,
    }
    result = VerificationResult(
        **body, hash_sha256=snapshot_hash(body), generated_at=utc_now()
    )
    receipt = AuditReceiptGenerator().generate_json_receipt(result)
    if result.verified or result.outcome != "unsupported":
        raise RuntimeError("Fixture safety invariant failed")
    return result, receipt

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="validate fixture offline without Streamlit")
    args = parser.parse_args()
    result, receipt = build_fixture()
    if args.smoke:
        print(f"DEMO_SMOKE_OK verified={result.verified} outcome={result.outcome} receipt_bytes={len(receipt.encode('utf-8'))}")
        return 0

    import streamlit as st
    st.set_page_config(page_title="Arc Verify — Fixture", page_icon="🧪")
    st.title("Offline fixture demonstration")
    st.error("FIXTURE ONLY — NOT ON-CHAIN — NOT VERIFIED")
    if st.button("Show clearly labeled sample"):
        st.json(result.model_dump(mode="json"))
        st.download_button(
            "Download fixture JSON (NOT VERIFIED)", receipt, "fixture-not-verified.json"
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
