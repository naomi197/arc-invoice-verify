"""
Demo runner: executes autonomous watchdog audit with live terminal visualization.
"""
from agent import AutonomousVerifierAgent, InvoiceTask
import json

def run_demo():
    print("=" * 70)
    print(" ARC INVOICE VERIFY - AUTONOMOUS AUDIT & CRE CONSENSUS DEMO")
    print("=" * 70)

    agent = AutonomousVerifierAgent()

    tasks = [
        InvoiceTask(
            invoice_id="INV-2026-001",
            expected_recipient="0x71c8fb86133757790b5340012299942c415a9999",
            expected_amount_usdc=1500.0,
            tx_hash="0x4e0a7f1a3b8d9c2e00112233445566778899aabbccddeeff0011223344556677",
        ),
        InvoiceTask(
            invoice_id="INV-2026-002",
            expected_recipient="0x71c8fb86133757790b5340012299942c415a9999",
            expected_amount_usdc=800.0,
            tx_hash="0x99887766554433221100ffeeddccbbaa99887766554433221100ffeeddccbbaa",
        ),
    ]

    mock_db = {
        "0x4e0a7f1a3b8d9c2e00112233445566778899aabbccddeeff0011223344556677": {
            "status": 1,
            "to": "0x71c8fb86133757790b5340012299942c415a9999",
            "amount_usdc": 1500.0,
        },
        "0x99887766554433221100ffeeddccbbaa99887766554433221100ffeeddccbbaa": {
            "status": 0,
            "to": "0x71c8fb86133757790b5340012299942c415a9999",
            "amount_usdc": 0.0,
        },
    }

    results = agent.run_autonomous_cycle(tasks, mock_rpc_data=mock_db)

    for res in results:
        badge = "[PASS - VERIFIED]" if res.verdict == "VERIFIED" else "[FAIL - REJECTED]"
        print(f"\n{badge} Invoice ID: {res.invoice_id}")
        print(f"Confidence: {res.confidence_score * 100:.1f}%")
        print(f"Court-Ready Evidence Hash: {res.evidence_hash}")
        print("Reasoning Trail:")
        for step in res.reasoning_trail:
            print(f"  -> {step}")

    print("\n" + "=" * 70)
    print(" Consensus payload ready for Chainlink CRE DON attestation.")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
