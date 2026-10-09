"""Compatibility adapter: delegates exclusively to shared RPC verifier."""
from dataclasses import dataclass, field
from typing import Any
from src.models import Invoice, VerificationResult
from src.arc_verify_core.verifier import ArcInvoiceVerifier

@dataclass
class InvoiceTask:
    invoice_id: str
    expected_recipient: str
    expected_amount_usdc: str
    tx_hash: str
    metadata: dict = field(default_factory=dict)

class AutonomousVerifierAgent:
    """No longer accepts a fabricated receipt amount; verifies via the same RPC core."""
    def __init__(self, verifier: ArcInvoiceVerifier | None = None):
        self.verifier = verifier or ArcInvoiceVerifier()

    def evaluate_task(self, task: InvoiceTask) -> VerificationResult:
        # payer must be explicitly supplied; no inferred/fabricated payer allowed.
        payer = task.metadata.get('payer_address')
        if not isinstance(payer, str):
            raise ValueError('metadata.payer_address is required for on-chain verification')
        invoice = Invoice(invoice_id=task.invoice_id, description=task.metadata.get('description','Invoice payment'),
                          recipient_address=task.expected_recipient, payer_address=payer,
                          amount_expected_usdc=task.expected_amount_usdc, currency_symbol='USDC')
        return self.verifier.verify_payment(invoice, task.tx_hash)
