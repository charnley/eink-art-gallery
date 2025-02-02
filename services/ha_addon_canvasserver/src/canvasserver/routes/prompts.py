from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..models.content import Images, Prompt, Prompts
from ..models.db import get_session

router = APIRouter(prefix="/prompts", tags=["prompt"])


@router.get("/", response_model=Prompts)
def read_items(limit=100):
    session = get_session()
    prompts = session.query(Prompt).limit(limit).all()
    return Prompts(prompts=prompts, count=len(prompts))


@router.get("/{id}", response_model=Prompt)
def get_item(id: str):
    session = get_session()
    item = session.get(Prompt, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/{id}/images", response_model=Images)
def get_item_childs(id: str):
    session = get_session()
    item = session.get(Prompt, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Find images
    # TODO
    images = []

    return Images(images=images, count=len(images))


@router.post("/")
def create_item(prompt: Prompt):
    session = get_session()

    prompt.id = None

    hash = Prompt.generate_id(prompt.prompt)

    existing_prompt = session.execute(
        select(Prompt).filter(Prompt.id == hash)
    ).scalar_one_or_none()

    if existing_prompt:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content already exists.")

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

    return prompt
