import uuid

from fastapi import APIRouter, HTTPException
from PIL import Image

from ..models.content import Image
from ..models.db import get_session

router = APIRouter(prefix="/actions")


def _generate_image(prompt):

    response = requests.post(external_api_url, json={"prompt": prompt})

    if response.status_code != 200:
        return None

    image_data = requests.get(image_url).content  # Get the image content

    return Image.Image


@router.get("/fill_queue/{promptId}", response_model=None, tags=["actions"])
def set_items(promptId):

    session = get_session()

    item = session.get(Prompt, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    text = prompt.prompt

    # Connect to model, and fetch. Really. Should I use redis queue?
    task_id = str(uuid.uuid4())  # Generate a unique task ID for this request

    background_tasks.add_task(_generate_image, prompt.prompt, task_id)

    task_status[task_id] = {"status": "processing", "image_url": None}

    return


# @router.get("/{id}", response_model=Prompt)
# def get_item(id: str):
#     session = get_session()
#     item = session.get(Prompt, id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item
