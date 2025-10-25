from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid1

from canvasserver.constants import IMAGE_CONTENT_TYPE
from canvasserver.models.db_models import Prompt
from canvasserver.models.schemas import ImageCreate, Images
from canvasserver.routes.displays import endpoint_queue
from canvasserver.routes.displays import prefix as displays_prefix
from canvasserver.routes.images import FILE_UPLOAD_KEY
from canvasserver.routes.images import prefix as image_prefix
from canvasserver.routes.prompts import prefix as prompt_prefix
from shared_constants import WaveshareDisplay
from shared_image_utils import image_to_bytes
from shared_matplotlib_utils import get_basic_text


def fetch_queue(tmp_client, url):
    response = tmp_client.get(url)
    return response.status_code


def test_new_prompt_new_images(tmp_client):
    """Test that multiple connections to the same sqlite database is okay"""

    # Create prompt
    prompt = Prompt(
        prompt="New And Fancy Prompt For Images, drawing, black and white",
        display_model=WaveshareDisplay.WaveShare13BlackWhite960x680,
        image_model="SD3",
        theme_id=None,
        active=True,
    )
    print(prompt)
    response1 = tmp_client.post(prompt_prefix, json=prompt.model_dump())
    print("response1", response1.json())
    assert response1.status_code == 200
    assert response1.json()

    # Validate response
    prompt_back = Prompt(**response1.json())
    prompt_id = prompt_back.id
    assert prompt_id is not None
    print(prompt_id)

    # Upload associated image to prompt create fake images
    n_new_images = 6
    images = []
    for i in range(n_new_images):
        images.append(get_basic_text(f"{uuid1()} - {i}"))
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

    # TODO Test prompt number of images

    # Run GET requests in parallel
    max_workers = 6
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                fetch_queue, tmp_client, displays_prefix + endpoint_queue + "?safe_http_code=False"
            )
            for _ in range(n_new_images)
        ]

        for future in as_completed(futures):
            assert future.result() == 200

    # Read images and count
    response_7 = tmp_client.get(image_prefix)
    print(response_7.json())
    assert response_7.status_code == 200
    images_respond_7 = Images(**response_7.json())
    assert images_respond_7.count == n_new_images - max_workers
