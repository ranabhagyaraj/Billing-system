from sqlalchemy.orm import Session
from app.models.models import Customer, Plan, Subscription, Invoice, PaymentAttempt, LedgerEntry

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_by_email(self, email: str):
        return self.db.query(Customer).filter(Customer.email == email).first()
    def create(self, name: str, email: str):
        cust = Customer(name=name, email=email)
        self.db.add(cust)
        self.db.commit()
        self.db.refresh(cust)
        return cust
    def get(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

class PlanRepository:
    def __init__(self, db: Session):
        self.db = db
    def get(self, plan_id: int):
        return self.db.query(Plan).filter(Plan.id == plan_id).first()
    def create(self, name: str, price: float, is_active: bool):
        plan = Plan(name=name, price=price, is_active=is_active)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db
    def get(self, sub_id: int):
        return self.db.query(Subscription).filter(Subscription.id == sub_id).first()
    def get_active_by_customer_and_plan(self, customer_id: int, plan_id: int):
        return self.db.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.plan_id == plan_id,
            Subscription.status == "active"
        ).first()
    def create(self, customer_id: int, plan_id: int, current_period_end):
        sub = Subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            current_period_end=current_period_end,
            status="active"
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db
    def get(self, invoice_id: int):
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    def create(self, subscription_id, customer_id, amount_due, currency, period_start, period_end, due_date):
        inv = Invoice(
            subscription_id=subscription_id,
            customer_id=customer_id,
            amount_due=amount_due,
            currency=currency,
            status="issued",
            period_start=period_start,
            period_end=period_end,
            due_date=due_date
        )
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(inv)
        return inv
    def save(self, invoice: Invoice):
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

class PaymentAttemptRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, invoice_id, amount, currency, status, provider_reference, failure_reason=None):
        attempt = PaymentAttempt(
            invoice_id=invoice_id,
            amount=amount,
            currency=currency,
            status=status,
            provider_reference=provider_reference,
            failure_reason=failure_reason
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

class LedgerRepository:
    def __init__(self, db: Session):
        self.db = db
    def create_entry(self, customer_id: int, event_type: str, reference_id: str, amount, currency="USD"):
        entry = LedgerEntry(
            customer_id=customer_id,
            event_type=event_type,
            reference_id=str(reference_id),
            amount=amount,
            currency=currency
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
