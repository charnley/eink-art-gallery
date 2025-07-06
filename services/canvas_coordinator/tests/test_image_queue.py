from uuid import uuid1

from canvasserver.constants import IMAGE_CONTENT_TYPE
from canvasserver.models.content import ImageCreate, Images, Prompt, Prompts
from canvasserver.routes.displays import endpoint_queue
from canvasserver.routes.displays import prefix as displays_prefix
from canvasserver.routes.images import FILE_UPLOAD_KEY
from canvasserver.routes.images import prefix as image_prefix
from canvasserver.routes.prompts import prefix as prompt_prefix
from PIL import Image as PilImage
from shared_constants import WaveshareDisplay
from shared_image_utils import bytes_to_image, image_to_bytes
from shared_matplotlib_utils import get_basic_text


def test_new_prompt_new_images(tmp_client):
    """Workflow test. Create new prompt and create new images"""

    # Baseline test, empty client
    response0 = tmp_client.get(prompt_prefix)
    print(response0.json())
    assert response0.json()["count"] == 0

    # Create prompt
    prompt = Prompt(
        prompt="New And Fancy Prompt For Images, drawing, black and white",
        display_model=WaveshareDisplay.WaveShare13BlackWhite960x680,
        theme_id=None,
        image_model="SD3",
    )
    response1 = tmp_client.post(prompt_prefix, json=prompt.model_dump())
    print("response1", response1.json())
    assert response1.status_code == 200
    assert response1.json()

    # Validate response
    prompt_back = Prompt(**response1.json())
    prompt_id = prompt_back.id
    assert prompt_id is not None

    # Check new prompt exists
    response2 = tmp_client.get(prompt_prefix)
    assert response2.status_code == 200
    prompts = Prompts(**response2.json())
    assert prompts.count == 1

    # Upload associated image to prompt
    # Create fake images
    n_new_images = 5
    images = []
    for i in range(n_new_images):
        images.append(get_basic_text(f"{uuid1()} - {i}"))

    # Search query
    files = [
        (FILE_UPLOAD_KEY, (f"file{i}", image_to_bytes(image), IMAGE_CONTENT_TYPE))
        for i, image in enumerate(images)
    ]
    params = ImageCreate(prompt=prompt_id)
    response3 = tmp_client.post(image_prefix, params=params.model_dump(), files=files)
    print(response3.json())
    assert response3.status_code == 200
    images_respond3 = Images(**response3.json())
    assert images_respond3.count == n_new_images

    # Read images and count
    response4 = tmp_client.get(image_prefix)
    print(response4.json())
    assert response4.status_code == 200
    images_respond = Images(**response4.json())
    assert images_respond.count == n_new_images

    # Read image that does not exist
    response_5a = tmp_client.get(image_prefix + f"/{uuid1()}")
    print(response_5a.json())
    assert response_5a.status_code == 404

    # Read image that does exist
    one_image_id = images_respond3.images[0].id
    response_5b = tmp_client.get(image_prefix + f"/{one_image_id}")
    assert response_5b.status_code == 200

    # Fetch queue five times
    for _ in range(n_new_images):
        # Fetch, not caring about active prompts
        response_6a = tmp_client.get(displays_prefix + endpoint_queue)
        assert response_6a.status_code == 200

        # Assert that is is picture
        image_6a = bytes_to_image(response_6a.content)
        assert isinstance(image_6a, PilImage.Image)

    response_6b = tmp_client.get(displays_prefix + endpoint_queue)
    assert response_6b.status_code == 200  # Empty, but still returns 200

    # Assert that is is picture
    image_6b = bytes_to_image(response_6b.content)
    assert isinstance(image_6b, PilImage.Image)

    # Read images and count
    response_7 = tmp_client.get(image_prefix)
    print(response_7.json())
    assert response_7.status_code == 200
    images_respond_7 = Images(**response_7.json())
    assert images_respond_7.count == 0
