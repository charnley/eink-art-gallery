from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from ..models.content import Image, Images, Prompt, Prompts
from ..models.db import get_session

prefix = "/prompts"
router = APIRouter(prefix=prefix, tags=["prompts"])


@router.get("/", response_model=Prompts)
def read_items(limit=100, session: Session = Depends(get_session)):
    prompts = session.query(Prompt).limit(limit).all()
    session.close()
    return Prompts(prompts=prompts, count=len(prompts))


@router.get("/{id}", response_model=Prompt)
def get_item(id: str, session: Session = Depends(get_session)):

    item = session.get(Prompt, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/{id}/images", response_model=Images)
def get_item_childs(id: str, session: Session = Depends(get_session)):

    prompt = session.get(Prompt, id)

    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    images = session.query(Image).filter(Image.prompt == prompt.id).all()
    session.close()

    return Images(images=images, count=len(images))


@router.delete("/{id}", response_model=Prompt)
def delete_item(id: str, session: Session = Depends(get_session)):
    item = session.get(Prompt, id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)

    # TODO Delete all Images to prompt also
    session.commit()
    session.close()

    return item


@router.post("/")
def create_item(prompt: Prompt, session: Session = Depends(get_session)):

    prompt.id = None

    hash = Prompt.generate_id(prompt.prompt)

    existing_prompt = session.execute(
        select(Prompt).filter(Prompt.id == hash)
    ).scalar_one_or_none()

    if existing_prompt:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content already exists.")

    # TODO Check with requests that it works and is alive

    session.add(prompt)

    try:
        session.commit()
        session.refresh(prompt)

    except ValueError:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the item.",
        )

    session.close()
    return prompt
