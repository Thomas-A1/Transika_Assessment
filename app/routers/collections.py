from fastapi import APIRouter
from .. import services
from ..schemas import CollectionInitiateRequest, CollectionResponse
from ..utils import iso

router = APIRouter(prefix="/collections", tags=["collections"])


def to_response(collection, status):
    return CollectionResponse(
        collection_id=collection["collection_id"],
        sender_id=collection["sender_id"],
        amount=collection["amount"],
        currency=collection["currency"],
        payment_method=collection["payment_method"],
        status=status,
        created_at=iso(collection["created_at"]),
    )


@router.post("/initiate", response_model=CollectionResponse, status_code=201)
def initiate_collection(payload: CollectionInitiateRequest):
    collection = services.create_collection(payload)
    return to_response(collection, collection["status"])


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(collection_id: str):
    collection = services.get_collection(collection_id)
    status = services.status_for(collection["created_at"])
    return to_response(collection, status)
