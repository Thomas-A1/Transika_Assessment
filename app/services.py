from datetime import timedelta
from . import config, storage
from .errors import (
    CollectionNotCompletedError,
    CollectionNotFoundError,
    QuoteExpiredError,
    QuoteNotFoundError,
    UnsupportedCorridorError,
    UnsupportedCurrencyError,
)
from .utils import iso, new_id, now_utc


def check_currency(currency):
    """
    Upper-case a currency and make sure we support it
    """
    code = currency.strip().upper()
    if code not in config.SUPPORTED_CURRENCIES:
        raise UnsupportedCurrencyError(code, sorted(config.SUPPORTED_CURRENCIES))
    return code


def status_for(created_at):
    """
    Work out a collection's status from how old it is
    """
    age = (now_utc() - created_at).total_seconds()
    if age >= config.COMPLETED_AFTER_SECONDS:
        return "completed"
    if age >= config.PROCESSING_AFTER_SECONDS:
        return "processing"
    return "pending"


def create_collection(req):
    currency = check_currency(req.currency)
    collection_id = new_id("col")
    collection = {
        "collection_id": collection_id,
        "sender_id": req.sender_id,
        "amount": round(float(req.amount), 2),
        "currency": currency,
        "payment_method": req.payment_method.value,
        "created_at": now_utc(),
        "status": "pending",
    }
    storage.collections[collection_id] = collection
    return collection


def get_collection(collection_id):
    collection = storage.collections.get(collection_id)
    if collection is None:
        raise CollectionNotFoundError(collection_id)
    return collection


def calculate_fee(amount):
    return round(max(amount * config.FEE_RATE, config.MIN_FEE_USD), 2)


def create_quote(req):
    from_currency = check_currency(req.from_currency)
    to_currency = check_currency(req.to_currency)
    corridor = from_currency + "-" + to_currency

    rate = config.EXCHANGE_RATES.get(corridor)
    if rate is None:
        raise UnsupportedCorridorError(corridor, sorted(config.EXCHANGE_RATES))

    amount = round(float(req.amount), 2)
    created_at = now_utc()
    quote_id = new_id("qte")
    quote = {
        "quote_id": quote_id,
        "corridor": corridor,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": rate,
        "converted_amount": round(amount * rate, 2),
        "fee_usd": calculate_fee(amount),
        "created_at": created_at,
        "rate_expires_at": created_at + timedelta(seconds=config.QUOTE_TTL_SECONDS),
    }
    storage.quotes[quote_id] = quote
    return quote


def get_quote(quote_id):
    quote = storage.quotes.get(quote_id)
    if quote is None:
        raise QuoteNotFoundError(quote_id)
    return quote


def execute_conversion(req):
    quote = get_quote(req.quote_id)
    collection = get_collection(req.collection_id)

    if now_utc() >= quote["rate_expires_at"]:
        raise QuoteExpiredError(quote["quote_id"], iso(quote["rate_expires_at"]))

    status = status_for(collection["created_at"])
    if status != "completed":
        raise CollectionNotCompletedError(collection["collection_id"], status)

    transfer_id = new_id("trf")
    transfer = {
        "transfer_id": transfer_id,
        "status": "processing",
        "quote_id": quote["quote_id"],
        "collection_id": collection["collection_id"],
        "conversion": {
            "corridor": quote["corridor"],
            "from_currency": quote["from_currency"],
            "to_currency": quote["to_currency"],
            "amount": quote["amount"],
            "exchange_rate": quote["exchange_rate"],
            "converted_amount": quote["converted_amount"],
            "fee_usd": quote["fee_usd"],
        },
        "created_at": now_utc(),
    }
    storage.transfers[transfer_id] = transfer
    return transfer
