"""Deterministic audit JSON and escaped PDF exports."""
from __future__ import annotations
import json
from pathlib import Path
from src.arc_verify_core.evidence import canonical_json, snapshot_hash

class AuditReceiptGenerator:
    def generate_audit_hash(self, result) -> str:
        return result.compute_hash()

    def generate_json_receipt(self, result, output_path=None) -> str:
        data=result.model_dump(mode='json')
        text=canonical_json(data)
        if output_path is not None:
            # Caller must provide a trusted destination. UI uses fixed in-memory output.
            Path(output_path).write_text(text+'\n',encoding='utf-8')
        return text

    def generate_pdf_receipt(self, result, output_path=None) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.utils import simpleSplit
            from reportlab.pdfgen import canvas
            import io
        except ImportError as exc:
            raise RuntimeError('Install reportlab to generate PDF receipts') from exc
        buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=letter)
        width,height=letter; y=height-48
        c.setTitle('Arc Invoice Verification Receipt')
        c.setFont('Helvetica-Bold',16); c.drawString(42,y,'Arc Invoice Verification Receipt'); y-=30
        rows=[('Outcome',result.outcome),('Verified',str(result.verified)),('Invoice ID',result.invoice.invoice_id),
              ('Description',result.invoice.description),('Transaction',result.tx_hash),
              ('Payer',result.invoice.payer_address),('Recipient',result.invoice.recipient_address),
              ('Expected USDC amount',result.invoice.amount_expected_usdc),('Chain ID',str(result.chain_id)),
              ('Reason',result.reason),('Snapshot SHA-256',result.hash_sha256),
              ('Issued (not hashed)',result.generated_at),
              ('Caveat','Integrity checksum only; not a signature, court-ready certificate, or ZK proof.')]
        c.setFont('Helvetica',9)
        for label,value in rows:
            text=f'{label}: {value}'
            for line in simpleSplit(text,'Helvetica',9,width-84):
                if y<55: c.showPage(); y=height-48; c.setFont('Helvetica',9)
                c.drawString(42,y,line); y-=14
        c.save(); data=buf.getvalue()
        if output_path is not None: Path(output_path).write_bytes(data)
        return data
