from agent import AutonomousVerifierAgent, InvoiceTask

def test_autonomous_agent_verified_flow():
    agent = AutonomousVerifierAgent()
    task = InvoiceTask(
        invoice_id="INV-001",
        expected_recipient="0x1111111111111111111111111111111111111111",
        expected_amount_usdc=250.0,
        tx_hash="0xabc123",
    )
    receipt = {
        "status": 1,
        "to": "0x1111111111111111111111111111111111111111",
        "amount_usdc": 250.0,
    }
    decision = agent.evaluate_task(task, receipt)
    assert decision.verdict == "VERIFIED"
    assert decision.confidence_score == 1.0
    assert len(decision.reasoning_trail) >= 4
    assert len(decision.evidence_hash) == 64

def test_autonomous_agent_rejection_flow():
    agent = AutonomousVerifierAgent()
    task = InvoiceTask(
        invoice_id="INV-002",
        expected_recipient="0x1111111111111111111111111111111111111111",
        expected_amount_usdc=500.0,
        tx_hash="0xfailed123",
    )
    receipt = {
        "status": 0,
        "to": "0x1111111111111111111111111111111111111111",
        "amount_usdc": 500.0,
    }
    decision = agent.evaluate_task(task, receipt)
    assert decision.verdict == "REJECTED"

def test_autonomous_cycle_runner():
    agent = AutonomousVerifierAgent()
    tasks = [
        InvoiceTask("INV-10", "0xabc", 100.0, "0xtx1"),
        InvoiceTask("INV-20", "0xabc", 200.0, "0xtx2"),
    ]
    mock_data = {
        "0xtx1": {"status": 1, "to": "0xabc", "amount_usdc": 100.0},
        "0xtx2": {"status": 1, "to": "0xwrong", "amount_usdc": 200.0},
    }
    results = agent.run_autonomous_cycle(tasks, mock_rpc_data=mock_data)
    assert len(results) == 2
    assert results[0].verdict == "VERIFIED"
    assert results[1].verdict == "REJECTED"
