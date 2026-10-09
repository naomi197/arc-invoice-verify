"""Validated invoice and result models."""
from pydantic import BaseModel,ConfigDict,field_validator,model_validator
class Invoice(BaseModel):
    model_config=ConfigDict(extra="forbid")
    invoice_id:str; description:str; recipient_address:str; payer_address:str; amount_expected_usdc:str; currency_symbol:str="USDC"
    @field_validator("invoice_id","currency_symbol","description")
    @classmethod
    def nonempty(cls,v):
        v=v.strip()
        if not v: raise ValueError("must not be empty")
        return v
    @field_validator("amount_expected_usdc")
    @classmethod
    def amount(cls,v):
        from src.arc_verify_core.money import parse_usdc_micro
        parse_usdc_micro(v); return str(v).strip()
    @field_validator("recipient_address","payer_address")
    @classmethod
    def addr(cls,v):
        import re
        if not isinstance(v,str) or not re.fullmatch(r"0x[0-9a-fA-F]{40}",v): raise ValueError("must be 20-byte hex address")
        return v
    @model_validator(mode="after")
    def different(self):
        if self.recipient_address.lower()==self.payer_address.lower(): raise ValueError("payer and recipient must differ")
        return self
class VerificationResult(BaseModel):
    model_config=ConfigDict(extra="forbid")
    invoice:Invoice; tx_hash:str; verified:bool; outcome:str; reason:str; policy:dict; evidence:dict; chain_id:int
    snapshot_version:str="arc-invoice-verify/3"; hash_sha256:str=""; generated_at:str=""
    def compute_hash(self):
        from src.arc_verify_core.evidence import snapshot_hash
        return snapshot_hash({"snapshot_version":self.snapshot_version,"invoice":self.invoice.model_dump(mode="json"),"tx_hash":self.tx_hash,"verified":self.verified,"outcome":self.outcome,"reason":self.reason,"policy":self.policy,"evidence":self.evidence,"chain_id":self.chain_id})
