from datetime import datetime
from fastapi import HTTPException
from decimal import Decimal

class InvoiceService:
    def __init__(self, subscription_repo, plan_repo, invoice_repo, ledger_repo):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.invoice_repo = invoice_repo
        self.ledger_repo = ledger_repo

    def generate_invoice(self, subscription_id: int, due_date: datetime):
        sub = self.subscription_repo.get(subscription_id)
        if not sub or sub.status != "active":
            raise HTTPException(status_code=400, detail="Subscription not found or inactive")
        
        plan = self.plan_repo.get(sub.plan_id)
        if not plan or not plan.is_active:
            raise HTTPException(status_code=400, detail="Plan is inactive or does not exist")

        amount_due = plan.price
        invoice = self.invoice_repo.create(
            subscription_id=sub.id,
            customer_id=sub.customer_id,
            amount_due=amount_due,
            currency="USD",
            period_start=sub.current_period_start,
            period_end=sub.current_period_end,
            due_date=due_date
        )

        self.ledger_repo.create_entry(
            customer_id=sub.customer_id,
            event_type="invoice_created",
            reference_id=str(invoice.id),
            amount=amount_due
        )
        return invoice

class PaymentService:
    def __init__(self, invoice_repo, payment_attempt_repo, ledger_repo):
        self.invoice_repo = invoice_repo
        self.payment_attempt_repo = payment_attempt_repo
        self.ledger_repo = ledger_repo

    def record_payment(self, invoice_id: int, amount: Decimal, status: str, provider_reference: str, failure_reason: str = None):
        invoice = self.invoice_repo.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        remaining_due = invoice.amount_due - invoice.amount_paid
        if status == "success" and amount > remaining_due:
            raise HTTPException(status_code=400, detail="Payment amount exceeds remaining unpaid invoice balance")

        attempt = self.payment_attempt_repo.create(
            invoice_id=invoice_id,
            amount=amount,
            currency=invoice.currency,
            status=status,
            provider_reference=provider_reference,
            failure_reason=failure_reason
        )

        if status == "success":
            invoice.amount_paid += amount
            if invoice.amount_paid >= invoice.amount_due:
                invoice.status = "paid"
            else:
                invoice.status = "partially_paid"
            self.invoice_repo.save(invoice)

            self.ledger_repo.create_entry(
                customer_id=invoice.customer_id,
                event_type="payment_success",
                reference_id=str(attempt.id),
                amount=amount,
                currency=invoice.currency
            )
        else:
            self.ledger_repo.create_entry(
                customer_id=invoice.customer_id,
                event_type="payment_failure",
                reference_id=str(attempt.id),
                amount=amount,
                currency=invoice.currency
            )

        return {"payment_attempt": attempt, "invoice": invoice}
