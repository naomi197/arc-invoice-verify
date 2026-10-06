import hashlib
import json
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .models import Invoice, VerificationResult


class AuditReceiptGenerator:
    """Generates immutable cryptographic audit certificates and PDF receipts for verified invoices."""

    @staticmethod
    def generate_audit_hash(invoice: Invoice, result: VerificationResult) -> str:
        payload = f"{invoice.invoice_id}:{result.tx_hash}:{result.block_number}:{result.status.value}:{result.amount_paid_wei}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def generate_json_receipt(cls, invoice: Invoice, result: VerificationResult, output_path: str) -> dict:
        audit_hash = cls.generate_audit_hash(invoice, result)
        receipt_data = {
            "certificate_title": "Arc Network On-Chain Payment Verification Certificate",
            "issuer": "Arc Invoice Verify (LegalTech Compliance Engine)",
            "issued_at_utc": datetime.now(timezone.utc).isoformat(),
            "audit_hash_sha256": audit_hash,
            "invoice": invoice.model_dump(),
            "verification": result.model_dump()
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(receipt_data, f, indent=2)
        return receipt_data

    @classmethod
    def generate_pdf_receipt(cls, invoice: Invoice, result: VerificationResult, output_pdf_path: str):
        audit_hash = cls.generate_audit_hash(invoice, result)
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=12
        )
        elements.append(Paragraph("<b>Arc Invoice Verify - Payment Certificate</b>", title_style))
        elements.append(Paragraph(f"<b>Verification Status:</b> <font color='{'#15803d' if result.is_valid else '#b91c1c'}'>{result.status.value}</font>", styles["Normal"]))
        elements.append(Paragraph(f"<b>Audit Hash (SHA-256):</b> <font size=8>{audit_hash}</font>", styles["Normal"]))
        elements.append(Spacer(1, 14))

        data = [
            ["Invoice ID", invoice.invoice_id],
            ["Description", invoice.description],
            ["Recipient Address", invoice.recipient_address],
            ["Expected Amount (Wei)", str(invoice.amount_expected_wei)],
            ["Transaction Hash", result.tx_hash],
            ["Block Number", str(result.block_number or "N/A")],
            ["Amount Paid (Wei)", str(result.amount_paid_wei or 0)],
            ["Payer / Sender", str(result.sender_address or "N/A")],
            ["Verification Note", result.details],
        ]

        table = Table(data, colWidths=[150, 390])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 16))
        footer_text = "<font size=8 color='#64748b'>Generated automatically by Arc Invoice Verify. Cryptographically verified against blockchain state. Read-only verification with zero private key exposure.</font>"
        elements.append(Paragraph(footer_text, styles["Normal"]))

        doc.build(elements)
