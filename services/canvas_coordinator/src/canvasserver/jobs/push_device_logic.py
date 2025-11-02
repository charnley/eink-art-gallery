import logging

from canvasserver.jobs.apis import send_image_to_frame
from canvasserver.models.db_models import Frame
from canvasserver.models.queries import fetch_image_for_frame
from canvasserver.models.schemas import FrameHttpCode
from shared_image_utils.displaying import prepare_image

logger = logging.getLogger(__name__)


def send_images_to_push_frames(session, frames: list[Frame]) -> list[FrameHttpCode]:

    returns = []

    for frame in frames:

        if frame.endpoint is None:
            continue

        image = fetch_image_for_frame(session, frame)
        image = prepare_image(image, frame.model)
        status_code = send_image_to_frame(image, frame)

        returns.append(FrameHttpCode(id=frame.id, status_code=status_code))

    return returns
