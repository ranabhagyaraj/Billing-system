from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.schemas import (
    CustomerCreate, CustomerResponse,
    PlanCreate, PlanResponse,
    SubscriptionCreate, SubscriptionResponse,
    InvoiceGenerateRequest, InvoiceResponse,
    PaymentRecordRequest
)
from app.repositories.repositories import (
    CustomerRepository, PlanRepository, SubscriptionRepository,
    InvoiceRepository, PaymentAttemptRepository, LedgerRepository
)
from app.services.services import InvoiceService, PaymentService

router = APIRouter()

@router.post("/customers", response_model=CustomerResponse)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    if repo.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Customer email must be unique")
    return repo.create(data.name, data.email)

@router.post("/plans", response_model=PlanResponse)
def create_plan(data: PlanCreate, db: Session = Depends(get_db)):
    repo = PlanRepository(db)
    return repo.create(data.name, data.price, data.is_active)

@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    cust_repo = CustomerRepository(db)
    if not cust_repo.get(data.customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    
    plan_repo = PlanRepository(db)
    plan = plan_repo.get(data.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=400, detail="Cannot create subscription for an inactive plan")

    sub_repo = SubscriptionRepository(db)
    existing = sub_repo.get_active_by_customer_and_plan(data.customer_id, data.plan_id)
    if existing:
        raise HTTPException(status_code=400, detail="Customer already has an active subscription to this plan")

    return sub_repo.create(data.customer_id, data.plan_id, data.current_period_end)

@router.post("/invoices/generate", response_model=InvoiceResponse)
def generate_invoice(data: InvoiceGenerateRequest, db: Session = Depends(get_db)):
    service = InvoiceService(
        SubscriptionRepository(db),
        PlanRepository(db),
        InvoiceRepository(db),
        LedgerRepository(db)
    )
    return service.generate_invoice(data.subscription_id, data.due_date)

@router.post("/payments")
def record_payment(data: PaymentRecordRequest, db: Session = Depends(get_db)):
    service = PaymentService(
        InvoiceRepository(db),
        PaymentAttemptRepository(db),
        LedgerRepository(db)
    )
    return service.record_payment(
        invoice_id=data.invoice_id,
        amount=data.amount,
        status=data.status,
        provider_reference=data.provider_reference,
        failure_reason=data.failure_reason
    )
