from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlmodel import select

from ..models.db import get_session
from ..models.db_models import Image, Prompt
from ..models.schemas import Images, Prompts, PromptStatus
from canvasserver.models.queries import find_prompts_with_missing_images

prefix = "/prompts"
router = APIRouter(prefix=prefix, tags=["prompts"])


prompt_filters = [None, "missing"]


@router.get("/", response_model=Prompts)
def read_items(
    limit=100,
    filter: str | None = Query(
        default=None,
        enum=prompt_filters,
    ),
    session: Session = Depends(get_session),
):

    if filter is None or filter == "null":
        prompts = session.query(Prompt).limit(limit).all()
        prompts = [PromptStatus(**prompt.dict()) for prompt in prompts]

    elif filter == "missing":
        prompts = find_prompts_with_missing_images(session)

    else:
        prompts = []

    return Prompts(prompts=prompts, count=len(prompts))

    session.close()


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

    images = session.query(Image).filter_by(prompt=id).all()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)

    for image in images:
        session.delete(image)

    session.commit()
    session.close()

    return item


@router.post("/")
def create_item(prompt: Prompt, session: Session = Depends(get_session)):

    # Check the prompt hash
    hash = Prompt.generate_id(prompt.prompt, prompt.display_model)
    existing_prompt = session.execute(
        select(Prompt).filter(Prompt.id == hash)
    ).scalar_one_or_none()

    if existing_prompt:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Content already exists.")

    prompt.id = hash
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
