"""Legacy smoke tests, adapted to the current fail-closed event-log verifier API."""
import unittest
from unittest.mock import MagicMock
from src.models import Invoice, VerificationResult
from src.arc_verify_core.verifier import ArcInvoiceVerifier, NetworkConfig, USDC_CONTRACT, TRANSFER_TOPIC0

H="0x"+"a"*64
ADDR_R="0x"+"1"*40; ADDR_P="0x"+"2"*40
def inv(amount="1.50"): return Invoice(invoice_id="INV-1",description="d",recipient_address=ADDR_R,payer_address=ADDR_P,amount_expected_usdc=amount)
def cfg(): return NetworkConfig("testnet","http://localhost",5042002,"x")
def rpc_ok(logs,finalized=None):
    resps={"eth_chainId":"0x4cef52","eth_getTransactionByHash":{"hash":H,"from":ADDR_P,"to":ADDR_R,"value":"0x0","input":"0x"},
           "eth_getTransactionReceipt":{"transactionHash":H,"status":"0x1","logs":logs},"eth_getCode":"0x"}
    if finalized is not None: resps["arc_getTransactionFinality"]={"finalized":finalized}
    class Rpc:
        def __init__(self,r): self.r=r
        def call(self,m,p): return self.r[m]
    return Rpc(resps)
def transfer_log(raw):
    return {"address":USDC_CONTRACT,"topics":[TRANSFER_TOPIC0,"0x"+"0"*24+ADDR_P[2:],"0x"+"0"*24+ADDR_R[2:]],"data":"0x"+format(raw,"064x"),"blockNumber":"0x1"}

class LegacyVerifier(unittest.TestCase):
    def test_verify_payment_success(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(1_500_000)],finalized=True))
        r=v.verify_payment(inv(),H)
        self.assertTrue(r.verified)
        self.assertEqual(r.outcome,"verified")
        self.assertEqual(r.evidence["matched_event"]["amount_usdc_micro"],"1500000")

    def test_verify_payment_insufficient_amount(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(1_000_000)]))
        r=v.verify_payment(inv("2.00"),H)
        self.assertFalse(r.verified)
        self.assertEqual(r.outcome,"insufficient")
        self.assertTrue(r.reason)

    def test_receipt_generation(self):
        import tempfile, os, json
        from src.receipt_generator import AuditReceiptGenerator
        i=inv("1.00")
        res=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(1_000_000)])).verify_payment(i,H)
        gen=AuditReceiptGenerator()
        with tempfile.TemporaryDirectory() as d:
            pf=os.path.join(d,"r.pdf"); jf=os.path.join(d,"r.json")
            gen.generate_pdf_receipt(res,pf)
            data=json.loads(gen.generate_json_receipt(res,jf))
            self.assertTrue(os.path.exists(pf))
            self.assertTrue(os.path.exists(jf))
            self.assertEqual(data["hash_sha256"],res.hash_sha256)

if __name__=="__main__": unittest.main()
