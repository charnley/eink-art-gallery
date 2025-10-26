import uuid

from canvasserver.models.db_models import Frame, FrameGroup, Image, Prompt
from shared_constants import WaveshareDisplay
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
    min_images: int
    image_count: int
    display_model: WaveshareDisplay


class PromptStatusResponse(Model):
    prompts: list[PromptStatus]
    count: int


class Prompts(Model):
    prompts: list[Prompt]
    count: int


class PromptQuery(Model):
    prompts: list[str]


class Frames(Model):
    frames: list[Frame]
    count: int


class FrameGroups(Model):
    groups: list[FrameGroup]
    count: int


class FrameGroupFrames(Model):
    group: FrameGroup
    frames: Frames


class FrameAssign(Model):
    id: uuid.UUID
