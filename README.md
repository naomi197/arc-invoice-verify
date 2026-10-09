# ⚖️ Arc Invoice Verify

**Read-only on-chain payment verification and audit-receipt generation for the Arc ecosystem.**

Built for the **Blockchain Legal Institute (BLI) Legal Tech Hackathon 2**.

## Overview

Arc Invoice Verify helps users compare commercial invoice terms with blockchain transaction data without requiring a wallet connection, transaction signing, or private-key access.

The application is designed as a read-only verification workflow:

1. Enter the expected invoice and payment details.
2. Retrieve or provide transaction information.
3. Compare the transaction against the invoice parameters.
4. Generate structured verification evidence.
5. Export an audit-oriented PDF receipt and JSON-compatible evidence.

The application is intended as a technical demonstration and verification aid. It does not provide legal advice and does not guarantee legal, regulatory, tax, accounting, or court acceptance.

## Key Features

- Read-only verification workflow
- No wallet connection or transaction-signing requirement
- Validation of recipient, sender, amount, transaction status, and confirmation data
- Integer-based amount handling to avoid floating-point rounding errors
- Deterministic evidence and hash generation
- PDF audit-receipt generation
- Structured verification results for downstream systems
- Streamlit interface for demonstration and review

## Architecture

- **Language:** Python
- **Blockchain integration:** web3.py and EVM-compatible RPC access
- **Data validation:** Pydantic
- **PDF generation:** ReportLab
- **User interface:** Streamlit
- **Testing:** pytest and Python unittest-compatible test modules

## Installation
```powershell
git clone https://github.com/naomi197/arc-invoice-verify.git
cd arc-invoice-verify
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

```

## Run the application


```powershell
streamlit run app.py

```

The local Streamlit address is normally displayed in the terminal after startup.

## Run tests


```powershell
pytest -v

```

The repository includes automated tests for the verification logic and related project components. Test success indicates that the covered scenarios passed; it should not be interpreted as a claim of 100% source-code coverage unless a coverage report is generated separately.

## Scope and limitations

- The application performs read-only verification and does not submit blockchain transactions.
- Verification results depend on the accuracy and availability of the configured RPC endpoint.
- Generated PDFs are audit-oriented technical records, not a legal opinion or a guarantee of court admissibility.
- The project does not claim to implement zero-knowledge proofs. The term “read-only” refers to the absence of wallet signing and write permissions.
- Users and organizations remain responsible for their own legal, tax, accounting, compliance, and evidentiary review.
- Live-network verification may require a configured RPC endpoint and network access.

## License

Distributed under the MIT License.
