import gzip
import io
import uuid
from datetime import datetime
from hashlib import sha256

from PIL import Image as PilImage
from pydantic import model_serializer
from shared_constants import IMAGE_FORMAT, WaveshareDisplay
from sqlalchemy import event
from sqlmodel import Field, LargeBinary
from sqlmodel import SQLModel as Model
from sqlmodel import TypeDecorator


def compress(s):
    if isinstance(s, str):
        s = s.encode()
    b = gzip.compress(s)
    return b


def decompress(b):
    s = gzip.decompress(b)
    return s


class ImageColumn(TypeDecorator):
    impl = LargeBinary

    @staticmethod
    def save_image(image):
        output = io.BytesIO()
        image.save(output, format=IMAGE_FORMAT)
        hex_data = output.getvalue()
        return hex_data

    @staticmethod
    def load_image(hex_data):
        image = PilImage.open(io.BytesIO(hex_data))
        return image

    def process_bind_param(self, value, dialect):
        return compress(self.save_image(value))

    def process_result_value(self, value, dialect):
        return self.load_image(decompress(value))


class Image(Model, table=True):
    __tablename__ = "image"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    prompt: str = Field(foreign_key="prompt.id", nullable=False, ondelete="CASCADE")
    image_data: bytes = Field(sa_column=LargeBinary)

    @property
    def image(self) -> PilImage.Image:
        return PilImage.open(io.BytesIO(self.image_data))

    @image.setter
    def image(self, image: PilImage.Image) -> None:
        output = io.BytesIO()
        image.save(output, format=IMAGE_FORMAT)
        hex_data = output.getvalue()
        self.image_data = hex_data
        # self.width, self.height = image.size

    @model_serializer
    def _ser(self) -> dict[str, str | float | int]:
        return {
            "id": str(self.id),
            "prompt": str(self.prompt),
        }

    def __str__(self) -> str:
        return f"Image(id={self.id},prompt={self.prompt})"

    def __repr__(self) -> str:
        return str(self)


class Images(Model):
    images: list[Image]
    count: int


class ImageCreate(Model):
    prompt: str


class ImageMeta(Model):
    prompt: str


class Prompt(Model, table=True):

    __tablename__: str = "prompt"

    id: str = Field(primary_key=True, default=None)
    prompt: str = Field()
    image_model: str = Field()
    min_images: int = Field(default=6, nullable=False)
    display_model: WaveshareDisplay = Field(nullable=False)

    active: bool = Field(default=False)
    theme_id: str | None = Field(foreign_key="theme.id", nullable=True)
    lifetime: datetime | None = Field(default=None, nullable=True)

    @staticmethod
    def generate_id(prompt_text: str) -> str:
        m = sha256()
        m.update(prompt_text.encode())
        return m.hexdigest()

    @model_serializer
    def _ser(self) -> dict[str, str | float | int]:
        return {
            "active": self.active,
            "id": str(self.id),
            "min_images": self.min_images,
            "image_model": str(self.image_model),
            "display_model": str(self.display_model),
            "prompt": str(self.prompt),
            # TODO Lifetime
        }

    def __str__(self) -> str:
        return f"Prompt(id={str(self.id):20s},active={str(self.active)})"

    def __repr__(self) -> str:
        return str(self)


@event.listens_for(Prompt, "before_insert")
def ensure_id_in_prompt(mapper, connection, target):
    if target.id is not None:
        return

    target.id = Prompt.generate_id(target.prompt)


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


class Theme(Model, table=True):
    __tablename__ = "theme"
    id: str = Field(primary_key=True, default=None)
    theme: str = Field()
    active: str = Field()

    @staticmethod
    def generate_id(text: str) -> str:
        m = sha256()
        m.update(text.encode())
        return m.hexdigest()


@event.listens_for(Theme, "before_insert")
def ensure_id_in_theme(mapper, connection, target):
    if target.id is not None:
        return
    target.id = Prompt.generate_id(target.theme)


class PushFrame(Model, table=True):
    __tablename__ = "frame_push"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hostname: str = Field(default="192.168.1.26:8080")
    model: WaveshareDisplay = Field()

    def __str__(self) -> str:
        return f"PushFrame(hostname={self.hostname},Model={self.model})"

    def __repr__(self) -> str:
        return str(self)


class PushFrames(Model):
    devices: list[PushFrame]
    count: int


class PullFrames(Model, table=True):
    __tablename__ = "reading_device"
    id: str = Field(primary_key=True)
    ip: str = Field()
    name: str = Field()
    model: WaveshareDisplay = Field()


class Queue(Model):
    id: str = Field(primary_key=True)


class Settings(Model):
    key: str = Field(primary_key=True)
    value: str = Field()
