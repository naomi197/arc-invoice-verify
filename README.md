# ⚖️ Arc Invoice Verify
> **Read-only, Zero-Knowledge On-Chain Payment Verification & Legal Audit Receipts for Arc Ecosystem**

Built for **Blockchain Legal Institute (BLI) Legal Tech Hackathon Edition 2**.

---

## 📌 Overview
Traditional crypto invoicing relies heavily on centralized payment processors or requires users to connect and grant broad wallet permissions, exposing private keys and transaction history to unnecessary risk.

**Arc Invoice Verify** provides an institutional-grade, **read-only verification engine** that validates on-chain settlements against legal commercial invoices without requiring wallet signatures, write permissions, or private key exposure. 

Once verified on Arc Mainnet, the engine cryptographically stamps and generates:
1. **Court-Ready PDF Audit Certificate** (with deterministic SHA-256 state hashes).
2. **Standardized JSON Audit Trail** for enterprise ERP / tax accounting systems.

---

## ⚡ Key Features
- **Zero-Wallet Connection (Read-Only)**: Verifies payments purely via state RPC calls to prevent phishing, drainage, and custodial liability.
- **Parametric Verification**: Validates expected recipient, sender restrictions, value in wei/ARC, block confirmations, and execution status.
- **Cryptographic Audit Proofs**: Every verification generates an immutable hash combining invoice terms and on-chain receipt metadata.
- **LegalTech Ready**: Output PDFs adhere to institutional auditing and cross-border commercial compliance standards.
- **Comprehensive Test Suite**: Built with 100% test coverage using pytest.

---

## 🏗️ Architecture & Stack
- **Language**: Python 3.12+
- **Blockchain Interface**: web3.py (EVM & Arc RPC Layer)
- **Data Modeling**: pydantic v2 (Strict schema validation)
- **Receipt Engine**: reportlab (Automated vector PDF generation)
- **User Interface**: streamlit
- **Testing**: pytest

---

## 🚀 Getting Started

### 1. Setup & Installation
```bash
git clone https://github.com/naomi197/arc-invoice-verify.git
cd arc-invoice-verify
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
streamlit run app.py
📜 License
Distributed under the MIT License.

