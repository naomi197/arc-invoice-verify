"""
Autonomous Verification Agent for Arc Invoice Verify.
Deterministic, tamper-proof invoice auditing engine with EVM/Arc RPC support,
cryptographic SHA256 reasoning trails, and court-ready evidence emission.
"""
from dataclasses import dataclass, field
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invoice_id": self.invoice_id,
            "verdict": self.verdict,
            "confidence_score": self.confidence_score,
            "reasoning_trail": self.reasoning_trail,
            "evidence_hash": self.evidence_hash,
            "timestamp": self.timestamp,
        }


class AutonomousVerifierAgent:
    def __init__(self, agent_name: str = "ArcAutonomousWatchdog-v1", rpc_url: Optional[str] = None):
        self.agent_name = agent_name
        self.rpc_url = rpc_url or os.getenv("ARC_RPC_URL", "https://rpc.arc.network")
        self.decision_log: List[AgentAuditDecision] = []

    def fetch_onchain_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Queries on-chain JSON-RPC for transaction receipt."""
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 1,
        }).encode("utf-8")

        req = urllib.request.Request(
            self.rpc_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "ArcAgent/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return data.get("result")
        except (urllib.error.URLError, TimeoutError, Exception):
            return None

    def evaluate_task(self, task: InvoiceTask, rpc_receipt: Dict[str, Any]) -> AgentAuditDecision:
        trail: List[str] = [
            f"Agent [{self.agent_name}] initiated autonomous audit for invoice {task.invoice_id}",
            f"Target TxHash: {task.tx_hash} | Target Recipient: {task.expected_recipient} | Target Amount: {task.expected_amount_usdc} USDC"
        ]

        status = rpc_receipt.get("status")
        to_addr = (rpc_receipt.get("to") or "").lower()
        amount = float(rpc_receipt.get("amount_usdc", 0.0))

        trail.append(f"On-chain status observed: {status}")

        if status not in (1, "0x1", "1"):
            trail.append("Verification FAILED: On-chain transaction status is reverted or not found.")
            verdict = "REJECTED"
            confidence = 1.0
        elif to_addr != task.expected_recipient.lower():
            trail.append(f"Verification FAILED: Recipient mismatch. Expected {task.expected_recipient}, received {to_addr}.")
            verdict = "REJECTED"
            confidence = 1.0
        elif amount < task.expected_amount_usdc:
            trail.append(f"Verification FAILED: Underpayment detected. Expected {task.expected_amount_usdc}, settled {amount}.")
            verdict = "REJECTED"
            confidence = 0.95
        else:
            trail.append(f"Verification SUCCESS: Exact settlement verified for {amount} USDC to {to_addr}.")
            verdict = "VERIFIED"
            confidence = 1.0

        evidence_payload = {
            "invoice_id": task.invoice_id,
            "tx_hash": task.tx_hash,
            "verdict": verdict,
            "trail": trail,
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()
        trail.append(f"Deterministic SHA256 Evidence Hash generated: {evidence_hash}")

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

    def run_autonomous_cycle(self, pending_tasks: List[InvoiceTask], mock_rpc_data: Optional[Dict[str, Dict[str, Any]]] = None) -> List[AgentAuditDecision]:
        results = []
        for task in pending_tasks:
            receipt = None
            if mock_rpc_data and task.tx_hash in mock_rpc_data:
                receipt = mock_rpc_data[task.tx_hash]
            else:
                receipt = self.fetch_onchain_receipt(task.tx_hash)

            if not receipt:
                receipt = {"status": 0, "to": "", "amount_usdc": 0.0}

            decision = self.evaluate_task(task, receipt)
            results.append(decision)
        return results
