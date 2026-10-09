import unittest
from src.models import Invoice,VerificationResult
from pydantic import ValidationError
class Models(unittest.TestCase):
    def test_ok(self):
        i=Invoice(invoice_id="A",description="d",recipient_address="0x"+"1"*40,payer_address="0x"+"2"*40,amount_expected_usdc="3.25"); self.assertEqual(i.currency_symbol,"USDC")
    def test_bad_addr(self): self.assertRaises(ValidationError,Invoice,invoice_id="A",description="d",recipient_address="0x123",payer_address="0x"+"2"*40,amount_expected_usdc="1")
    def test_same_parties(self): self.assertRaises(ValidationError,Invoice,invoice_id="A",description="d",recipient_address="0x"+"1"*40,payer_address="0x"+"1"*40,amount_expected_usdc="1")
    def test_bad_amount(self): self.assertRaises(ValidationError,Invoice,invoice_id="A",description="d",recipient_address="0x"+"1"*40,payer_address="0x"+"2"*40,amount_expected_usdc="1.0000001")
    def test_hash_deterministic(self):
        i=Invoice(invoice_id="A",description="d",recipient_address="0x"+"1"*40,payer_address="0x"+"2"*40,amount_expected_usdc="1")
        r1=VerificationResult(invoice=i,tx_hash="0x"+"a"*64,verified=False,outcome="unsupported",reason="x",policy={},evidence={},chain_id=5042)
        self.assertEqual(r1.compute_hash(),r1.compute_hash())
        self.assertEqual(r1.snapshot_version,"arc-invoice-verify/3")
