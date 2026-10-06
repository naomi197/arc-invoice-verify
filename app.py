import os
import streamlit as st
from src.models import Invoice, InvoiceStatus
from src.verifier import ArcInvoiceVerifier
from src.receipt_generator import AuditReceiptGenerator

st.set_page_config(
    page_title="Arc Invoice Verify | LegalTech Engine",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Arc Invoice Verify")
st.caption("Read-only, Zero-Knowledge On-Chain Payment Verification & Legal Audit Receipts for Arc Mainnet")

st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Invoice Details")
    invoice_id = st.text_input("Invoice ID", value="INV-2026-BLI-001")
    description = st.text_input("Service Description", value="Legal Tech Consulting & Smart Contract Audit")
    recipient_address = st.text_input("Expected Recipient Address (EVM)", value="0x71C7656EC7ab88b098defB751B7401B5f6d8976F")
    payer_address = st.text_input("Expected Payer Address (Optional)", value="")
    
    amount_in_arc = st.number_input("Expected Amount (ARC)", min_value=0.0001, value=1.5, step=0.1, format="%.4f")
    amount_expected_wei = int(amount_in_arc * (10 ** 18))

    st.subheader("2. Arc Network Configuration")
    rpc_url = st.text_input("RPC Endpoint", value="https://rpc.arc.network")

with col2:
    st.subheader("3. On-Chain Verification")
    tx_hash = st.text_input("Transaction Hash (0x...)", placeholder="Paste Arc Mainnet Transaction Hash here")
    
    verify_button = st.button("🔍 Verify Transaction & Generate Audit Certificate", type="primary", use_container_width=True)

    if verify_button:
        if not tx_hash.strip():
            st.warning("⚠️ Please provide a valid transaction hash.")
        else:
            invoice = Invoice(
                invoice_id=invoice_id,
                recipient_address=recipient_address,
                payer_address=payer_address if payer_address.strip() else None,
                amount_expected_wei=amount_expected_wei,
                description=description
            )
            
            verifier = ArcInvoiceVerifier(rpc_url=rpc_url)
            
            with st.spinner("Querying blockchain state..."):
                result = verifier.verify_payment(invoice, tx_hash.strip())

            if result.is_valid:
                st.success(f"✅ Verified Successfully! (Block: {result.block_number})")
            else:
                st.error(f"❌ Verification Failed: {result.status.value}")
                st.info(f"Reason: {result.details}")

            # Generate Audit Receipts
            os.makedirs("exports", exist_ok=True)
            pdf_path = f"exports/{invoice.invoice_id}_certificate.pdf"
            json_path = f"exports/{invoice.invoice_id}_certificate.json"
            
            AuditReceiptGenerator.generate_pdf_receipt(invoice, result, pdf_path)
            AuditReceiptGenerator.generate_json_receipt(invoice, result, json_path)

            st.markdown("### 📄 Cryptographic Receipts")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Legal PDF Certificate",
                    data=f,
                    file_name=f"{invoice.invoice_id}_Audit_Certificate.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with open(json_path, "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Download JSON Audit Trail",
                    data=f.read(),
                    file_name=f"{invoice.invoice_id}_Audit_Trail.json",
                    mime="application/json",
                    use_container_width=True
                )

st.markdown("---")
st.markdown("<center><small style='color: gray;'>Built for BLI Legal Tech Hackathon 2026 | Read-Only | Compliance & Audit Ready</small></center>", unsafe_allow_html=True)
