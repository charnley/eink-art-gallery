from uuid import uuid1

from canvasserver.constants import IMAGE_CONTENT_TYPE
from canvasserver.models.db_models import Frame, FrameGroup, FrameType, Prompt
from canvasserver.models.schemas import FrameAssign, ImageCreate, Images, Prompts
from canvasserver.routes.frames import prefix as frames_prefix
from canvasserver.routes.groups import prefix as groups_prefix
from canvasserver.routes.images import FILE_UPLOAD_KEY
from canvasserver.routes.images import prefix as image_prefix
from canvasserver.routes.prompts import prefix as prompt_prefix
from PIL import Image as PilImage
from shared_constants import WaveshareDisplay
from shared_image_utils import bytes_to_image, image_to_bytes
from shared_matplotlib_utils import get_basic_text

DISPLAY_MODEL = WaveshareDisplay.WaveShare13BlackWhite960x680
FRAME_MAC = "aa:bb:cc:dd:ee:ff"
FRAME_USER_AGENT = f"Frame/{DISPLAY_MODEL}"


def test_new_prompt_new_images(tmp_client):
    """Workflow test. Create new prompt and create new images"""

    # Baseline test, empty client
    response0 = tmp_client.get(prompt_prefix)
    assert Prompts(**response0.json()).count == 0

    # Setup: group
    group = FrameGroup(name="TestGroup", default=True)
    response = tmp_client.post(
        groups_prefix + "/", json=group.model_dump(mode="json", exclude={"id", "frames"})
    )
    assert response.status_code == 200
    group = FrameGroup(**response.json())

    # Setup: frame assigned to group
    frame = Frame(mac=FRAME_MAC, model=DISPLAY_MODEL, type=FrameType.PULL)
    response = tmp_client.post(
        frames_prefix + "/",
        json=frame.model_dump(mode="json", exclude={"id", "group", "group_id", "endpoint"}),
    )
    assert response.status_code == 200
    frame = Frame(**response.json())

    response = tmp_client.post(
        f"{groups_prefix}/{group.id}/frames", json=FrameAssign(id=frame.id).model_dump(mode="json")
    )
    assert response.status_code == 200

    # Create prompt(s)
    prompt = Prompt(
        prompt="New And Fancy Prompt For Images, drawing, black and white",
        display_model=DISPLAY_MODEL,
        image_model="SD3",
    )
    response1 = tmp_client.post(prompt_prefix, json=prompt.model_dump())
    print("response1", response1.json())
    assert response1.status_code == 200
    assert response1.json()

    prompt = Prompt(**response1.json())
    assert prompt.id is not None

    # Create a second prompt to verify only the empty one gets deleted
    prompt2 = Prompt(
        prompt="A second prompt that will not be consumed",
        display_model=DISPLAY_MODEL,
        image_model="SD3",
    )
    response_p2 = tmp_client.post(prompt_prefix, json=prompt2.model_dump())
    assert response_p2.status_code == 200
    prompt2 = Prompt(**response_p2.json())

    # Check new prompts exist
    response2 = tmp_client.get(prompt_prefix)
    assert response2.status_code == 200
    prompts = Prompts(**response2.json())
    assert prompts.count == 2

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
    params = ImageCreate(prompt=prompt.id)
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

    # Activate prompt for the group before fetching
    response_rotate = tmp_client.post(f"{groups_prefix}/{group.id}/prompts/rotate")
    assert response_rotate.status_code == 200

    # Fetch queue five times via the frame endpoint
    for _ in range(n_new_images):
        response_6a = tmp_client.get(
            f"{frames_prefix}/by-mac/{frame.mac}/display.png",
            headers={"user-agent": FRAME_USER_AGENT},
        )
        assert response_6a.status_code == 200
        assert isinstance(bytes_to_image(response_6a.content), PilImage.Image)

    response_6b = tmp_client.get(
        f"{frames_prefix}/by-mac/{frame.mac}/display.png",
        headers={"user-agent": FRAME_USER_AGENT},
    )
    assert response_6b.status_code == 200
    assert isinstance(bytes_to_image(response_6b.content), PilImage.Image)

    # Read images and count
    response_7 = tmp_client.get(image_prefix)
    print(response_7.json())
    assert response_7.status_code == 200
    images_respond_7 = Images(**response_7.json())
    assert images_respond_7.count == 0

    # Prompt 1 is automatically deleted when its last image is consumed
    assert tmp_client.get(f"{prompt_prefix}/{prompt.id}").status_code == 404

    # Prompt 2 is unaffected
    assert tmp_client.get(f"{prompt_prefix}/{prompt2.id}").status_code == 200
