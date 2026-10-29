from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, condecimal

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class PlanCreate(BaseModel):
    name: str
    price: condecimal(gt=0)
    is_active: bool = True

class PlanResponse(PlanCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int
    current_period_end: datetime

class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    plan_id: int
    status: str
    current_period_start: datetime
    current_period_end: datetime
    class Config:
        from_attributes = True

class InvoiceGenerateRequest(BaseModel):
    subscription_id: int
    due_date: datetime

class InvoiceResponse(BaseModel):
    id: int
    subscription_id: int
    customer_id: int
    amount_due: float
    amount_paid: float
    currency: str
    status: str
    period_start: datetime
    period_end: datetime
    due_date: datetime
    class Config:
        from_attributes = True

class PaymentRecordRequest(BaseModel):
    invoice_id: int
    amount: condecimal(gt=0)
    currency: str = "USD"
    status: str
    provider_reference: str
    failure_reason: Optional[str] = None
