import uuid
from io import BytesIO

from canvasserver.constants import IMAGE_EXTENSION, IMAGE_HEADER
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from PIL import Image as PilImage
from shared_image_utils import dithering, image_to_bytes
from sqlalchemy.orm import Session

from ..models.db import get_session
from ..models.db_models import Image, Prompt
from ..models.schemas import ImageCreate, Images

prefix = "/images"
router = APIRouter(prefix=prefix, tags=["images"])

FILE_UPLOAD_KEY = "files"


@router.get("/", response_model=Images)
def read_items(limit=100, session: Session = Depends(get_session)):
    images = session.query(Image).limit(limit).all()
    session.close()
    return Images(images=images, count=len(images))


@router.get("/{id}", response_model=Image)
def read_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(Image, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{id}", response_model=Image)
def delete_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(Image, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
    session.close()

    return item


@router.get(
    "/{id}/display." + f"{IMAGE_EXTENSION}",
    responses={200: {"content": {f"image/{IMAGE_EXTENSION}": {}}}},
    response_class=Response,
)
async def read_item_png(
    id: uuid.UUID, use_dithering: bool = False, session: Session = Depends(get_session)
):

    item = session.get(Image, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    image = item.image
    if use_dithering:
        image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=f"image/{IMAGE_EXTENSION}")


@router.post("/")
async def create_items(
    base: ImageCreate = Depends(),
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
) -> Images:

    if base.prompt is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to specify owner of image",
        )

    # TODO Check disk-size limitations

    id = base.prompt
    prompt = session.get(Prompt, id)
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner was not found",
        )

    images: list[Image] = []

    for file in files:
        readable = BytesIO(file.file.read())
        image_image = PilImage.open(readable)

        image = Image(prompt=prompt.id)
        image.image = image_image

        images.append(image)
        session.add(image)

    try:
        session.commit()
        session.refresh(prompt)

    except Exception as e:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving images. {e}",
        )

    return Images(images=images, count=len(images))
