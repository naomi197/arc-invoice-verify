from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED_MISMATCH = "FAILED_MISMATCH"
    FAILED_REVERTED = "FAILED_REVERTED"
    NOT_FOUND = "NOT_FOUND"


class Invoice(BaseModel):
    """Invoice data model"""
    invoice_id: str = Field(..., description="Unique invoice identifier, e.g. INV-2026-001")
    recipient_address: str = Field(..., description="EVM address expected to receive the payment")
    payer_address: Optional[str] = Field(None, description="Optional expected payer EVM address")
    amount_expected_wei: int = Field(..., description="Expected payment amount in WEI")
    currency_symbol: str = Field(default="ARC", description="Symbol of native token")
    description: str = Field(default="Professional Services", description="Service description")
    due_timestamp: Optional[int] = Field(None, description="Unix timestamp expiration")


class VerificationResult(BaseModel):
    """Verification outcome"""
    invoice_id: str
    tx_hash: str
    status: InvoiceStatus
    is_valid: bool
    block_number: Optional[int] = None
    sender_address: Optional[str] = None
    receiver_address: Optional[str] = None
    amount_paid_wei: Optional[int] = None
    currency_symbol: str = "ARC"
    explorer_url: Optional[str] = None
    details: str = ""
