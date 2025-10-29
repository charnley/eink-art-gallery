import uuid

from canvasserver.models.db_models import Frame, FrameGroup, Image
from shared_constants import FrameType, WaveshareDisplay
from sqlmodel import SQLModel as Model


class FrameHttpCode(Model):
    id: uuid.UUID
    status_code: int


class Images(Model):
    images: list[Image]
    count: int


class ImageCreate(Model):
    prompt: str


class ImageMeta(Model):
    prompt: str


class PromptStatus(Model):
    id: str
    prompt: str
    image_model: str
    display_model: WaveshareDisplay

    # Computed properties
    count_images: int | None = None
    count_frames: int | None = None


class PromptStatusResponse(Model):
    prompts: list[PromptStatus]
    count: int


class Prompts(Model):
    prompts: list[PromptStatus]
    count: int


class PromptQuery(Model):
    prompts: list[str]


class PromptId(Model):
    prompt_id: str


class Frames(Model):
    frames: list[Frame]
    count: int


class FrameGroups(Model):
    groups: list[FrameGroup]
    count: int


class FrameGroupFrames(Model):
    group: FrameGroup
    frames: Frames


class FrameGroupUpdate(Model):
    name: str | None = None
    schedule_frame: str | None = None
    schedule_prompt: str | None = None
    default: bool | None = None


class FrameAssign(Model):
    id: uuid.UUID


class FrameUpdate(Model):
    type: FrameType | None = None
    model: WaveshareDisplay | None = None
    mac: str | None = None
    endpoint: str | None = None
    group_id: uuid.UUID | None = None
