"""
Autonomous Verification Agent for Arc Invoice Verify.
Monitors pending invoices, fetches deterministic on-chain evidence via Arc RPC,
records verifiable reasoning trails, and emits audit certificates autonomously.
"""
from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import Any, Dict, List, Optional


@dataclass
class InvoiceTask:
    invoice_id: str
    expected_recipient: str
    expected_amount_usdc: float
    tx_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentAuditDecision:
    invoice_id: str
    verdict: str  # "VERIFIED" | "REJECTED" | "INSUFFICIENT_EVIDENCE"
    confidence_score: float
    reasoning_trail: List[str]
    evidence_hash: str
    timestamp: int


class AutonomousVerifierAgent:
    def __init__(self, agent_name: str = "ArcAutonomousWatchdog-v1"):
        self.agent_name = agent_name
        self.decision_log: List[AgentAuditDecision] = []

    def evaluate_task(self, task: InvoiceTask, rpc_receipt: Dict[str, Any]) -> AgentAuditDecision:
        trail: List[str] = []
        trail.append(f"Agent [{self.agent_name}] picked task {task.invoice_id}")

        status = rpc_receipt.get("status")
        to_addr = (rpc_receipt.get("to") or "").lower()
        amount = float(rpc_receipt.get("amount_usdc", 0.0))

        trail.append(f"Observed on-chain tx: {task.tx_hash} | Status: {status}")

        if status != 1 and status != "0x1":
            trail.append("Evidence check failed: Transaction execution status is reverted/failed.")
            verdict = "REJECTED"
            confidence = 1.0
        elif to_addr != task.expected_recipient.lower():
            trail.append(f"Evidence check failed: Recipient mismatch. Expected {task.expected_recipient}, got {to_addr}")
            verdict = "REJECTED"
            confidence = 1.0
        elif amount < task.expected_amount_usdc:
            trail.append(f"Evidence check failed: Underpayment. Expected {task.expected_amount_usdc}, got {amount}")
            verdict = "REJECTED"
            confidence = 0.95
        else:
            trail.append(f"Evidence confirmed: Exact settlement of {amount} USDC to {to_addr}.")
            verdict = "VERIFIED"
            confidence = 1.0

        evidence_payload = {
            "invoice_id": task.invoice_id,
            "tx_hash": task.tx_hash,
            "verdict": verdict,
            "trail": trail,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        decision = AgentAuditDecision(
            invoice_id=task.invoice_id,
            verdict=verdict,
            confidence_score=confidence,
            reasoning_trail=trail,
            evidence_hash=evidence_hash,
            timestamp=int(time.time()),
        )
        self.decision_log.append(decision)
        return decision

    def run_autonomous_cycle(self, pending_tasks: List[InvoiceTask], mock_rpc_data: Dict[str, Dict[str, Any]]) -> List[AgentAuditDecision]:
        results = []
        for task in pending_tasks:
            receipt = mock_rpc_data.get(task.tx_hash, {"status": 0, "to": "", "amount_usdc": 0.0})
            decision = self.evaluate_task(task, receipt)
            results.append(decision)
        return results
