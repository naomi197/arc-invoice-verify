from typing import Optional
from web3 import Web3
from .models import Invoice, InvoiceStatus, VerificationResult


class ArcInvoiceVerifier:
    """Read-only on-chain verifier for Arc / EVM transactions."""

    def __init__(self, rpc_url: str = "https://rpc.arc.network", explorer_base_url: str = "https://explorer.arc.network/tx/"):
        self.rpc_url = rpc_url
        self.explorer_base_url = explorer_base_url
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def verify_payment(self, invoice: Invoice, tx_hash: str) -> VerificationResult:
        """
        Fetches the transaction and its receipt, verifies receiver and amount.
        Returns a structured VerificationResult.
        """
        clean_tx_hash = tx_hash.strip()
        explorer_url = f"{self.explorer_base_url}{clean_tx_hash}"

        try:
            tx = self.w3.eth.get_transaction(clean_tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(clean_tx_hash)
        except Exception as e:
            return VerificationResult(
                invoice_id=invoice.invoice_id,
                tx_hash=clean_tx_hash,
                status=InvoiceStatus.NOT_FOUND,
                is_valid=False,
                explorer_url=explorer_url,
                details=f"Transaction not found or RPC error: {str(e)}"
            )

        # Check transaction execution status (1 = success, 0 = reverted)
        if receipt.get("status") != 1:
            return VerificationResult(
                invoice_id=invoice.invoice_id,
                tx_hash=clean_tx_hash,
                status=InvoiceStatus.FAILED_REVERTED,
                is_valid=False,
                block_number=receipt.get("blockNumber"),
                sender_address=tx.get("from"),
                receiver_address=tx.get("to"),
                amount_paid_wei=tx.get("value"),
                currency_symbol=invoice.currency_symbol,
                explorer_url=explorer_url,
                details="Transaction was reverted on-chain."
            )

        sender = tx.get("from", "").lower()
        receiver = (tx.get("to") or "").lower()
        amount_paid = tx.get("value", 0)
        expected_receiver = invoice.recipient_address.lower()

        # Check receiver
        if receiver != expected_receiver:
            return VerificationResult(
                invoice_id=invoice.invoice_id,
                tx_hash=clean_tx_hash,
                status=InvoiceStatus.FAILED_MISMATCH,
                is_valid=False,
                block_number=receipt.get("blockNumber"),
                sender_address=tx.get("from"),
                receiver_address=tx.get("to"),
                amount_paid_wei=amount_paid,
                currency_symbol=invoice.currency_symbol,
                explorer_url=explorer_url,
                details=f"Recipient mismatch: expected {invoice.recipient_address}, got {tx.get('to')}"
            )

        # Check amount
        if amount_paid < invoice.amount_expected_wei:
            return VerificationResult(
                invoice_id=invoice.invoice_id,
                tx_hash=clean_tx_hash,
                status=InvoiceStatus.FAILED_MISMATCH,
                is_valid=False,
                block_number=receipt.get("blockNumber"),
                sender_address=tx.get("from"),
                receiver_address=tx.get("to"),
                amount_paid_wei=amount_paid,
                currency_symbol=invoice.currency_symbol,
                explorer_url=explorer_url,
                details=f"Insufficient payment: expected {invoice.amount_expected_wei} Wei, got {amount_paid} Wei"
            )

        # Check payer (if specified in invoice)
        if invoice.payer_address and sender != invoice.payer_address.lower():
            return VerificationResult(
                invoice_id=invoice.invoice_id,
                tx_hash=clean_tx_hash,
                status=InvoiceStatus.FAILED_MISMATCH,
                is_valid=False,
                block_number=receipt.get("blockNumber"),
                sender_address=tx.get("from"),
                receiver_address=tx.get("to"),
                amount_paid_wei=amount_paid,
                currency_symbol=invoice.currency_symbol,
                explorer_url=explorer_url,
                details=f"Payer mismatch: expected {invoice.payer_address}, got {tx.get('from')}"
            )

        return VerificationResult(
            invoice_id=invoice.invoice_id,
            tx_hash=clean_tx_hash,
            status=InvoiceStatus.VERIFIED,
            is_valid=True,
            block_number=receipt.get("blockNumber"),
            sender_address=tx.get("from"),
            receiver_address=tx.get("to"),
            amount_paid_wei=amount_paid,
            currency_symbol=invoice.currency_symbol,
            explorer_url=explorer_url,
            details="Payment successfully verified on-chain."
        )
