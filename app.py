"""Streamlit UI; importing this module is safe when Streamlit is not installed."""
try:
    import streamlit as st
except ImportError:
    st = None


def main():
    if st is None:
        raise RuntimeError("Streamlit is required to run this UI; install requirements.txt")
    from pydantic import ValidationError
    from src.models import Invoice
    from src.arc_verify_core.verifier import ArcInvoiceVerifier, NetworkConfig
    from src.receipt_generator import AuditReceiptGenerator

    st.set_page_config(page_title="Arc Invoice Verify", page_icon="◈", layout="wide")
    st.title("Arc Invoice Verify")
    st.caption("USDC payment evidence on Arc · Read-only RPC · No wallet keys")
    st.warning("Verification uses Transfer event logs. Invoice association is user-supplied and is not proven on-chain.")
    with st.expander("Unit and scope details", expanded=True):
        st.markdown("""**USDC amounts use 6 decimals.** Native Arc Transfer event values use 18 decimals and are converted only when exactly divisible by 10¹²; native dust is rejected, never rounded. ERC-20 USDC logs use 6-decimal units. Transaction `value` alone does not prove payment.

No legal/evidentiary guarantee, signature, court-ready certificate, or ZK proof is provided. Verification depends on configured RPC; finality is shown only when the RPC provides a supported signal.""")
    if "last_result" not in st.session_state: st.session_state.last_result = None
    if "last_input" not in st.session_state: st.session_state.last_input = None
    a, b = st.columns(2)
    with a:
        st.subheader("Invoice")
        iid=st.text_input("Invoice ID"); desc=st.text_input("Description"); recipient=st.text_input("Recipient address"); payer=st.text_input("Expected payer address")
        amount=st.text_input("Expected USDC amount", help="Plain decimal string, maximum 6 fractional digits; no float conversions.")
        currency=st.text_input("Currency", value="USDC")
    with b:
        st.subheader("Transaction")
        txh=st.text_input("Transaction hash"); exact=st.checkbox("Require exact amount (otherwise overpayment accepted)", False)
        cfg=NetworkConfig.from_env(); st.info(f"Network: **{cfg.name}** · expected chain ID **{cfg.expected_chain_id}**")
        st.caption("RPC endpoint is server-side. Live eth_chainId is checked on every verification.")
        verify=st.button("Verify events", type="primary", use_container_width=True)
    vals=(iid,desc,recipient,payer,amount,currency,txh,exact)
    if st.session_state.last_input is not None and vals != st.session_state.last_input: st.session_state.last_result=None
    if verify:
        st.session_state.last_input=vals
        try:
            inv=Invoice(invoice_id=iid, description=desc, recipient_address=recipient, payer_address=payer, amount_expected_usdc=amount, currency_symbol=currency)
            with st.spinner("Querying configured Arc RPC…"): result=ArcInvoiceVerifier(cfg, exact_amount=exact).verify_payment(inv, txh)
            st.session_state.last_result=result
        except (ValidationError, ValueError) as e:
            st.session_state.last_result=None; st.error(f"Invalid input: {e}")
        except Exception:
            st.session_state.last_result=None; st.error("Verification unavailable; no payment was verified. Check server logs.")
    result=st.session_state.last_result
    if result is not None:
        (st.success if result.verified else st.info if result.outcome in ("pending", "not_found") else st.error)(f"{result.outcome.upper()}: {result.reason}")
        st.write(f"Chain ID: `{result.chain_id}` · Invoice: `{result.invoice.invoice_id}`")
        st.json({"policy":result.policy, "evidence":result.evidence})
        st.caption(f"Evidence snapshot SHA-256: `{result.hash_sha256}` — integrity checksum only, not a signature or independent trust proof.")
        gen=AuditReceiptGenerator()
        st.download_button("Download JSON evidence", gen.generate_json_receipt(result), "arc-verification-evidence.json", "application/json")
        st.download_button("Download PDF summary", gen.generate_pdf_receipt(result), "arc-verification-summary.pdf", "application/pdf")
    st.caption("RPC results are not independently audited. A detected event does not establish invoice authenticity, legal enforceability, or non-reuse of a transaction.")


if __name__ == "__main__":
    main()
