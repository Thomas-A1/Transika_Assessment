"""
Request and response models.
"""

from enum import Enum
from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    mobile_money = "mobile_money"
    bank_transfer = "bank_transfer"


class CollectionStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"


class CollectionInitiateRequest(BaseModel):
    model_config = {"extra": "forbid"}
    sender_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=1)
    payment_method: PaymentMethod


class CollectionResponse(BaseModel):
    collection_id: str
    sender_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: CollectionStatus
    created_at: str


class ConversionQuoteRequest(BaseModel):
    model_config = {"extra": "forbid"}
    from_currency: str = Field(min_length=1)
    to_currency: str = Field(min_length=1)
    amount: float = Field(gt=0)


class QuoteResponse(BaseModel):
    quote_id: str
    corridor: str
    from_currency: str
    to_currency: str
    amount: float
    exchange_rate: float
    converted_amount: float
    fee_usd: float
    rate_expires_at: str
    created_at: str


class ConversionExecuteRequest(BaseModel):
    model_config = {"extra": "forbid"}
    quote_id: str = Field(min_length=1)
    collection_id: str = Field(min_length=1)


class ConversionDetails(BaseModel):
    corridor: str
    from_currency: str
    to_currency: str
    amount: float
    exchange_rate: float
    converted_amount: float
    fee_usd: float


class TransferResponse(BaseModel):
    transfer_id: str
    status: str
    quote_id: str
    collection_id: str
    conversion: ConversionDetails
    created_at: str
