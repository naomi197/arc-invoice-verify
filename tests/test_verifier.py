from unittest.mock import MagicMock
from src.models import Invoice, InvoiceStatus
from src.verifier import ArcInvoiceVerifier


def test_verify_payment_success():
    verifier = ArcInvoiceVerifier()
    verifier.w3 = MagicMock()

    invoice = Invoice(
        invoice_id="INV-2026-001",
        recipient_address="0x1111111111111111111111111111111111111111",
        payer_address="0x2222222222222222222222222222222222222222",
        amount_expected_wei=1000000000000000000,
        currency_symbol="ARC"
    )

    verifier.w3.eth.get_transaction.return_value = {
        "from": "0x2222222222222222222222222222222222222222",
        "to": "0x1111111111111111111111111111111111111111",
        "value": 1000000000000000000
    }
    verifier.w3.eth.get_transaction_receipt.return_value = {
        "status": 1,
        "blockNumber": 123456
    }

    result = verifier.verify_payment(invoice, "0xabcdef1234567890")

    assert result.is_valid is True
    assert result.status == InvoiceStatus.VERIFIED
    assert result.block_number == 123456


def test_verify_payment_insufficient_amount():
    verifier = ArcInvoiceVerifier()
    verifier.w3 = MagicMock()

    invoice = Invoice(
        invoice_id="INV-2026-002",
        recipient_address="0x1111111111111111111111111111111111111111",
        amount_expected_wei=2000000000000000000
    )

    verifier.w3.eth.get_transaction.return_value = {
        "from": "0x2222222222222222222222222222222222222222",
        "to": "0x1111111111111111111111111111111111111111",
        "value": 1000000000000000000
    }
    verifier.w3.eth.get_transaction_receipt.return_value = {
        "status": 1,
        "blockNumber": 123457
    }

    result = verifier.verify_payment(invoice, "0xabcdef1234567891")

    assert result.is_valid is False
    assert result.status == InvoiceStatus.FAILED_MISMATCH
    assert "Insufficient payment" in result.details


def test_receipt_generation(tmp_path):
    from src.receipt_generator import AuditReceiptGenerator
    from src.models import InvoiceStatus, VerificationResult

    invoice = Invoice(
        invoice_id="INV-2026-TEST",
        recipient_address="0x1111111111111111111111111111111111111111",
        amount_expected_wei=1000000000000000000,
        description="Legal Consulting"
    )

    result = VerificationResult(
        invoice_id=invoice.invoice_id,
        tx_hash="0xabc123",
        status=InvoiceStatus.VERIFIED,
        is_valid=True,
        block_number=99999,
        sender_address="0x2222222222222222222222222222222222222222",
        receiver_address="0x1111111111111111111111111111111111111111",
        amount_paid_wei=1000000000000000000,
        details="Verified"
    )

    pdf_file = tmp_path / "test_receipt.pdf"
    json_file = tmp_path / "test_receipt.json"

    AuditReceiptGenerator.generate_pdf_receipt(invoice, result, str(pdf_file))
    json_data = AuditReceiptGenerator.generate_json_receipt(invoice, result, str(json_file))

    assert pdf_file.exists()
    assert json_file.exists()
    assert "audit_hash_sha256" in json_data
