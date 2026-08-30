from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid1

from canvasserver.constants import IMAGE_CONTENT_TYPE
from canvasserver.models.db_models import Frame, FrameGroup, FrameType, Prompt
from canvasserver.models.schemas import FrameAssign, ImageCreate, Images
from canvasserver.routes.frames import prefix as frames_prefix
from canvasserver.routes.groups import prefix as groups_prefix
from canvasserver.routes.images import FILE_UPLOAD_KEY
from canvasserver.routes.images import prefix as image_prefix
from canvasserver.routes.prompts import prefix as prompt_prefix
from shared_constants import WaveshareDisplay
from shared_image_utils import image_to_bytes
from shared_matplotlib_utils import get_basic_text

DISPLAY_MODEL = WaveshareDisplay.WaveShare13BlackWhite960x680
FRAME_USER_AGENT = f"Frame/{DISPLAY_MODEL}"


def fetch_frame(tmp_client, mac):
    response = tmp_client.get(
        f"{frames_prefix}/by-mac/{mac}/display.png",
        headers={"user-agent": FRAME_USER_AGENT},
    )
    return response.status_code


def test_concurrent_frames(tmp_client):
    """Test that multiple frames hitting the server concurrently is safe (no race conditions)"""

    # Setup: group
    group = FrameGroup(name="TestGroup", default=True)
    response = tmp_client.post(
        groups_prefix + "/", json=group.model_dump(mode="json", exclude={"id", "frames"})
    )
    assert response.status_code == 200
    group = FrameGroup(**response.json())

    # Setup: one frame per worker, all in the same group
    n_frames = 6
    frame_macs = [f"aa:bb:cc:dd:ee:{i:02x}" for i in range(n_frames)]
    for mac in frame_macs:
        frame = Frame(mac=mac, model=DISPLAY_MODEL, type=FrameType.PULL)
        response = tmp_client.post(
            frames_prefix + "/",
            json=frame.model_dump(mode="json", exclude={"id", "group", "group_id", "endpoint"}),
        )
        assert response.status_code == 200
        frame = Frame(**response.json())

        response = tmp_client.post(
            f"{groups_prefix}/{group.id}/frames",
            json=FrameAssign(id=frame.id).model_dump(mode="json"),
        )
        assert response.status_code == 200

    # Create prompt
    prompt = Prompt(
        prompt="New And Fancy Prompt For Images, drawing, black and white",
        display_model=DISPLAY_MODEL,
        image_model="SD3",
    )
    response1 = tmp_client.post(prompt_prefix, json=prompt.model_dump())
    assert response1.status_code == 200
    prompt = Prompt(**response1.json())
    assert prompt.id is not None

    # Upload one image per frame
    n_new_images = n_frames
    images = [get_basic_text(f"{uuid1()} - {i}") for i in range(n_new_images)]
    files = [
        (FILE_UPLOAD_KEY, (f"file{i}", image_to_bytes(image), IMAGE_CONTENT_TYPE))
        for i, image in enumerate(images)
    ]
    response3 = tmp_client.post(
        image_prefix, params=ImageCreate(prompt=prompt.id).model_dump(), files=files
    )
    assert response3.status_code == 200
    assert Images(**response3.json()).count == n_new_images

    # Activate prompt for the group
    response_rotate = tmp_client.post(f"{groups_prefix}/{group.id}/prompts/rotate")
    assert response_rotate.status_code == 200

    # All frames fetch concurrently — each should get a unique image
    with ThreadPoolExecutor(max_workers=n_frames) as executor:
        futures = [executor.submit(fetch_frame, tmp_client, mac) for mac in frame_macs]
        for future in as_completed(futures):
            assert future.result() == 200

    # All images consumed
    assert Images(**tmp_client.get(image_prefix).json()).count == 0

    # Prompt is automatically deleted when its last image is consumed
    assert tmp_client.get(f"{prompt_prefix}/{prompt.id}").status_code == 404
