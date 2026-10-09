# DoraHacks listing — paste this into build 49390

Track: LegalTech & RegTech.

Do not apply the RYO-CHAN market-agent bounty with this repository. Do not apply the Chainlink CRE bounty unless a workflow has been simulated or deployed with the CRE CLI. This repository does not contain that workflow.

## Short description

Read-only Arc USDC checker: enter an invoice and a transaction hash, and see whether the receipt contains an ERC-20 Transfer from the configured USDC contract for that payer, recipient, and amount. No wallet, no signing, and no private keys. Native transfers and transaction value are not treated as payment.

## About

Arc Invoice Verify compares a user-supplied USDC invoice with a transaction on the configured Arc network. The default network is testnet (chain ID 5042002). Mainnet (chain ID 5042) is selected only with ARC_NETWORK=mainnet. Every check reads eth_chainId from the RPC and rejects a mismatch.

A payment is accepted only when the receipt succeeded and contains an ERC-20 Transfer from the configured USDC contract (0x3600000000000000000000000000000000000000) whose sender, recipient, and 6-decimal amount satisfy the invoice. Overpayment is accepted unless the operator requires an exact amount. Two smaller transfers in one transaction are not added together.

Native Transfer logs and the transaction value field are stored as extra evidence. They do not verify a USDC invoice. Finality is shown only when the RPC method arc_getTransactionFinality returns a boolean. Otherwise the result says finality is unknown.

The invoice id is not written on-chain. Matching a transfer does not prove that this invoice is the one the payer intended, and the same transaction can match another invoice with the same payer, recipient, and amount. The SHA-256 value on the result is an integrity checksum of the evidence snapshot. It is not a signature, a zero-knowledge proof, or a statement that a court, auditor, or tax authority will accept the file.

### What it does

- Builds an invoice in the browser session: id, description, payer, recipient, and a decimal USDC amount with at most 6 fractional digits.
- Reads the transaction and receipt from the configured public Arc RPC. The demo does not ask for a wallet, a signature, or a seed phrase.
- Checks chain id, receipt success, and one qualifying USDC Transfer.
- Exports a JSON evidence file and a PDF summary that repeat the same limits.

### Why Arc

Arc uses USDC as its gas token. This prototype answers a narrower question than "was gas paid": did this receipt include a USDC token Transfer that matches the invoice terms the operator typed. The check is read-only.

### Links

- Live demo: https://arc-invoice-verify-j3g4khgxrzqtlbxssjkyy6.streamlit.app/
- Source: https://github.com/naomi197/arc-invoice-verify
- Developer: https://github.com/naomi197

Replace the live-demo line if that deployment is still running an older build that credited native transfers. Publish this revision first, then update the link.

### Before resubmitting

- Confirm the DoraHacks member profile resolves. The build page has been showing "Hacker does not exist".
- Add two screenshots: one verified USDC Transfer, and one rejected native transfer or underpayment.
