# Arc Invoice Verify

> **Deterministic On-Chain Invoice Verification, Autonomous Watchdog Agent & Chainlink CRE Workflow**  > Submitted to **BLI Legal Tech Hackathon 2 (DoraHacks)**

---

## 🏇 Targeted Hackathon Bounties

1. **Autonomous Agents ($6,000 - Sponsored by ROO-CHAN)**
   - Implements `AutonomousVerifierAgent` (`agent.py`) that monitors pending settlements, cross-references transaction telemetry, and generates digitally verifiable "Reasoning Trails" for tamper-proof provenance.
2. **Best workflow with CRE ($2,000 - Sponsored by Chainlink)**
   - Implements Chainlink Runtime Environment specification (`cre-workflow/project.yaml`, `cre-workflow/workflow.ts`) to achieve BFT node consensus across DON networks before emitting court-ready audit certificates.

---

## 🏇 Architecture Overview

events: [Invoice Settlement] -> [Arc / EVM On-Chain Tx] -> [Autonomous Watchdog Agent] -> [Chainlink CRE Consensus (DON)] -> [Court-Ready Audit Certificate]

---

## 🙩 Quickstart & Reproduction

```bash
# Run Autonomous Watchdog Demo
python demo.py

# Run Test Suite
python -m pytest -v
```

---

## 📂 Project Structure

```
 agent.py              # Autonomous Verification Agent Engine
 demo.py              # Live CLI demonstration runner
 cre-workflow/
     project.yaml       # Chainlink CRE configuration & BFT consensus
     workflow.ts        # TypeScript CRE consensus logic
 tests/
     test_agent.py      # Unit & integration tests
 README.md
 ```

## ⚖️ License
MIT License. Built for LITE Legal Tech Hackathon 2.
