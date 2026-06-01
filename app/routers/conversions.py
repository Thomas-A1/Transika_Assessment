from fastapi import APIRouter

from .. import services
from ..schemas import (
    ConversionDetails,
    ConversionExecuteRequest,
    ConversionQuoteRequest,
    QuoteResponse,
    TransferResponse,
)
from ..utils import iso

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.post("/quote", response_model=QuoteResponse)
def create_quote(payload: ConversionQuoteRequest):
    quote = services.create_quote(payload)
    return QuoteResponse(
        quote_id=quote["quote_id"],
        corridor=quote["corridor"],
        from_currency=quote["from_currency"],
        to_currency=quote["to_currency"],
        amount=quote["amount"],
        exchange_rate=quote["exchange_rate"],
        converted_amount=quote["converted_amount"],
        fee_usd=quote["fee_usd"],
        rate_expires_at=iso(quote["rate_expires_at"]),
        created_at=iso(quote["created_at"]),
    )


@router.post("/execute", response_model=TransferResponse)
def execute_conversion(payload: ConversionExecuteRequest):
    transfer = services.execute_conversion(payload)
    return TransferResponse(
        transfer_id=transfer["transfer_id"],
        status=transfer["status"],
        quote_id=transfer["quote_id"],
        collection_id=transfer["collection_id"],
        conversion=ConversionDetails(**transfer["conversion"]),
        created_at=iso(transfer["created_at"]),
    )
