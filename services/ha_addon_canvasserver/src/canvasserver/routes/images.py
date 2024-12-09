import uuid

from fastapi import APIRouter, HTTPException

from ..models.content import Image, Images
from ..models.db import get_session

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/", response_model=Images)
def read_items(limit=100):

    session = get_session()
    images = session.query(Image).all()
    return images


@router.get("/{id}", response_model=Image)
def read_item(id: uuid.UUID):
    """Get Image by ID"""
    item = session.get(Image, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item
