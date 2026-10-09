import unittest
from src.models import Invoice
from src.arc_verify_core.verifier import ArcInvoiceVerifier,NetworkConfig,USDC_CONTRACT,NATIVE_EMITTER,TRANSFER_TOPIC0
class Rpc:
    def __init__(self,resps): self.resps=resps; self.calls=[]
    def call(self,m,p):
        self.calls.append(m)
        if m not in self.resps:
            from src.arc_verify_core.rpc import RpcError
            raise RpcError("method unavailable")
        return self.resps[m]
H="0x"+"a"*64
ADDR_R="0x"+"1"*40; ADDR_P="0x"+"2"*40; ADDR_X="0x"+"3"*40
def inv(): return Invoice(invoice_id="I-1",description="d",recipient_address=ADDR_R,payer_address=ADDR_P,amount_expected_usdc="1.50")
def cfg(): return NetworkConfig("testnet","http://localhost",5042002,"x")
def transfer_log(emitter,sender,recipient,raw_data):
    return {"address":emitter,"topics":[TRANSFER_TOPIC0,"0x"+"0"*24+sender[2:],"0x"+"0"*24+recipient[2:]],"data":"0x"+format(raw_data,"064x"),"blockNumber":"0x1"}
def rpc_ok(logs,finalized=None):
    resps={"eth_chainId":"0x4cef52","eth_getTransactionByHash":{"hash":H,"from":ADDR_P,"to":ADDR_X,"value":"0x0","input":"0x"},
           "eth_getTransactionReceipt":{"transactionHash":H,"status":"0x1","logs":logs},
           "eth_getCode":"0x"}
    if finalized is not None: resps["arc_getTransactionFinality"]={"finalized":finalized}
    return Rpc(resps)
class Verifier(unittest.TestCase):
    def test_native_exact_divisible_verified(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(NATIVE_EMITTER,ADDR_P,ADDR_R,1_500_000*10**12)]))
        r=v.verify_payment(inv(),H); self.assertTrue(r.verified); self.assertEqual(r.evidence["matched_event"]["amount_usdc_micro"],"1500000")
    def test_native_dust_unsupported(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(NATIVE_EMITTER,ADDR_P,ADDR_R,1_500_000*10**12+7)]))
        r=v.verify_payment(inv(),H); self.assertFalse(r.verified); self.assertEqual(r.outcome,"unsupported"); self.assertIn("precision",r.reason)
    def test_native_dust_accept_policy(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(NATIVE_EMITTER,ADDR_P,ADDR_R,1_500_000*10**12+7)]),accept_dust=True)
        r=v.verify_payment(inv(),H); self.assertFalse(r.verified); self.assertEqual(r.outcome,"insufficient"); self.assertIn("dust",r.reason)
        self.assertEqual(r.evidence["dust"]["dust_base_units"],"7")
        self.assertEqual(r.evidence["dust"]["expected_native_raw_minimum"],str(1_500_000*10**12))
        self.assertTrue(r.evidence["dust"]["raw_meets_invoice_threshold"])
    def test_native_dust_below_invoice_never_rounds_up(self):
        raw=1_500_000*10**12-1
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(NATIVE_EMITTER,ADDR_P,ADDR_R,raw)]),accept_dust=True)
        r=v.verify_payment(inv(),H)
        self.assertFalse(r.verified); self.assertEqual(r.outcome,"insufficient")
        self.assertFalse(r.evidence["dust"]["raw_meets_invoice_threshold"])
        self.assertEqual(r.evidence["dust"]["dust_base_units"],str(10**12-1))
    def test_erc20_verified(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(USDC_CONTRACT,ADDR_P,ADDR_R,1_500_000)]))
        r=v.verify_payment(inv(),H); self.assertTrue(r.verified); self.assertEqual(r.evidence["matched_event"]["kind"],"erc20")
    def test_erc20_wrong_recipient(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(USDC_CONTRACT,ADDR_P,ADDR_X,1_500_000)]))
        r=v.verify_payment(inv(),H); self.assertFalse(r.verified); self.assertEqual(r.outcome,"insufficient")
    def test_no_logs_value_ignored(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([])); r=v.verify_payment(inv(),H)
        self.assertFalse(r.verified); self.assertIn("tx.value",r.reason)
    def test_wrong_chain(self):
        rp=rpc_ok([]); rp.resps["eth_chainId"]="0x1"
        r=ArcInvoiceVerifier(cfg(),rp).verify_payment(inv(),H); self.assertEqual(r.outcome,"unsupported")
    def test_reverted(self):
        rp=rpc_ok([transfer_log(USDC_CONTRACT,ADDR_P,ADDR_R,1_500_000)]); rp.resps["eth_getTransactionReceipt"]["status"]="0x0"
        r=ArcInvoiceVerifier(cfg(),rp).verify_payment(inv(),H); self.assertEqual(r.outcome,"insufficient")
    def test_unknown_emitter_ignored(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log("0x"+"9"*40,ADDR_P,ADDR_R,1_500_000)]))
        r=v.verify_payment(inv(),H); self.assertEqual(r.outcome,"unsupported")
    def test_wrong_configured_chain_id(self):
        rp=rpc_ok([]); rp.resps["eth_chainId"]="0x13b2" # mainnet while config is testnet
        r=ArcInvoiceVerifier(cfg(),rp).verify_payment(inv(),H)
        self.assertEqual(r.outcome,"unsupported")
    def test_non_usdc_invoice_rejected(self):
        i=Invoice(invoice_id="I",description="d",recipient_address=ADDR_R,payer_address=ADDR_P,amount_expected_usdc="1",currency_symbol="ARC")
        rp=rpc_ok([])
        r=ArcInvoiceVerifier(cfg(),rp).verify_payment(i,H)
        self.assertEqual(r.outcome,"invalid_request")
        self.assertNotIn("eth_getTransactionByHash",rp.calls)
    def test_bad_hash(self):
        r=ArcInvoiceVerifier(cfg(),rpc_ok([])).verify_payment(inv(),"0x123")
        self.assertEqual(r.outcome,"invalid_request")
    def test_finality_reported(self):
        v=ArcInvoiceVerifier(cfg(),rpc_ok([transfer_log(USDC_CONTRACT,ADDR_P,ADDR_R,1_500_000)],finalized=True))
        r=v.verify_payment(inv(),H); self.assertTrue(r.verified); self.assertEqual(r.evidence["finality"]["finalized"],True)
    def test_finality_unavailable_not_claimed(self):
        class NoFin(Rpc):
            def call(self,m,p):
                if m=="arc_getTransactionFinality": from src.arc_verify_core.rpc import RpcError; raise RpcError("no method")
                return super().call(m,p)
        r=ArcInvoiceVerifier(cfg(),NoFin(rpc_ok([transfer_log(USDC_CONTRACT,ADDR_P,ADDR_R,1_500_000)]).resps)).verify_payment(inv(),H)
        self.assertIsNone(r.evidence["finality"]["finalized"])
    def test_malformed_log_fails_closed(self):
        bad={"address":USDC_CONTRACT,"topics":[TRANSFER_TOPIC0,"0xshort","0x"+"0"*64],"data":"0x"+"0"*64}
        r=ArcInvoiceVerifier(cfg(),rpc_ok([bad])).verify_payment(inv(),H); self.assertEqual(r.outcome,"insufficient")
