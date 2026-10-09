import unittest
from agent.agent import AutonomousVerifierAgent, InvoiceTask
from src.models import VerificationResult

class StubVerifier:
    def verify_payment(self, invoice, tx_hash):
        self.invoice, self.tx_hash = invoice, tx_hash
        return VerificationResult(invoice=invoice, tx_hash=tx_hash, verified=False, outcome="unsupported", reason="stub", policy={}, evidence={}, chain_id=5042002)

class AgentAdapter(unittest.TestCase):
    def test_task_maps_usdc_amount_to_invoice_field(self):
        stub=StubVerifier(); task=InvoiceTask("i-1", "0x"+"1"*40, "1.25", "0x"+"a"*64, {"payer_address":"0x"+"2"*40})
        result=AutonomousVerifierAgent(stub).evaluate_task(task)
        self.assertEqual(stub.invoice.amount_expected_usdc, "1.25")
        self.assertEqual(stub.tx_hash, task.tx_hash)
        self.assertEqual(result.outcome, "unsupported")
    def test_missing_payer_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "payer_address"):
            AutonomousVerifierAgent(StubVerifier()).evaluate_task(InvoiceTask("i", "0x"+"1"*40,"1", "0x"+"a"*64))

if __name__ == "__main__": unittest.main()
