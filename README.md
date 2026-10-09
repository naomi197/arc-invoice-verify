# Arc Invoice Verify

Read-only check of whether an Arc transaction contains a USDC ERC-20 `Transfer` that matches an invoice. Built for the Blockchain Legal Institute (BLI) Legal Tech Hackathon 2.

## What a match means

A result is `verified` only when all of the following are true:

- The invoice currency is USDC.
- The configured RPC `eth_chainId` matches the selected Arc network (testnet `5042002` or mainnet `5042`).
- The transaction hash on the transaction and on the receipt is the hash that was requested.
- The receipt status is success (`1`).
- The receipt contains an ERC-20 `Transfer` from the configured USDC contract, `0x3600000000000000000000000000000000000000`.
- That log's sender, recipient, and amount satisfy the invoice. Overpayment is accepted unless exact amount is required.

Native Transfer logs and `transaction.value` are kept in the evidence object and are not payment. Finality is reported only when `arc_getTransactionFinality` returns a boolean. If that call is missing, finality is unknown and is not treated as confirmed.

The invoice id is supplied by the user. It is not bound to the transaction on-chain, so the same payment can match more than one invoice that shares the payer, recipient, and amount. The SHA-256 snapshot hash is an integrity checksum of the result body. It is not a signature, a zero-knowledge proof, or a court certificate.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The default network is testnet. Set `ARC_NETWORK` to `mainnet` or `testnet`, and set `ARC_RPC_URL` only when you need an endpoint other than the public Arc RPC for that network.

## Tests

```powershell
pytest -v
```

Passing tests cover the scenarios in `tests/`. They are not a claim of complete coverage.

## Layout

- `app.py` — Streamlit demonstration
- `demo.py` — offline fixture that is always unverified
- `src/arc_verify_core/` — RPC client, decimal parsing, and the verifier
- `src/models.py` — invoice and result models
- `src/receipt_generator.py` — JSON and PDF export
- `tests/` — the only test suite
- `docs/dorahacks-listing.md` — text to paste into the DoraHacks build page

## License

MIT
