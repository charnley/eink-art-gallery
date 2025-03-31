import gzip
import io
import uuid
from hashlib import sha256

from PIL import Image as PilImage
from pydantic import model_serializer
from sqlalchemy import event
from sqlmodel import Field, LargeBinary
from sqlmodel import SQLModel as Model
from sqlmodel import TypeDecorator

from ..constants import IMAGE_FORMAT


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
    width: int = Field()
    height: int = Field()

    @property
    def image(self) -> PilImage.Image:
        return PilImage.open(io.BytesIO(self.image_data))

    @image.setter
    def image(self, image: PilImage.Image) -> None:
        output = io.BytesIO()
        image.save(output, format=IMAGE_FORMAT)
        hex_data = output.getvalue()
        self.image_data = hex_data
        self.width, self.height = image.size

    @model_serializer
    def _ser(self) -> dict[str, str | float | int]:
        return {
            "id": str(self.id),
            "prompt": str(self.prompt),
            "width": self.width,
            "height": self.height,
        }

    def __str__(self) -> str:
        return f"Image(id={self.id},prompt={self.prompt})"

    def __repr__(self) -> str:
        return f"Image(id={self.id},prompt={self.prompt})"


class Images(Model):
    images: list[Image]
    count: int


class ImageCreate(Model):
    prompt: str


class ImageMeta(Model):
    prompt: str


class Prompt(Model, table=True):
    __tablename__ = "prompt"

    id: str = Field(primary_key=True, default=None)
    prompt: str = Field()
    model: str = Field()

    active: bool = Field(default=False)
    theme_id: str = Field(foreign_key="theme.id", nullable=True)

    # lifetime: DateTime = Field()  # TODO Implement lifetime
    # lifetime: DateTime = Field(nullable=True, default=func.now()) # + one month or so

    @staticmethod
    def generate_id(prompt_text: str) -> str:
        m = sha256()
        m.update(prompt_text.encode())
        return m.hexdigest()

    def __repr__(self) -> str:
        return f"Prompt(id={self.id:20s},active={self.active})"

    def __str__(self) -> str:
        return f"Prompt(id={self.id:20s},active={self.active})"


@event.listens_for(Prompt, "before_insert")
def ensure_id_in_prompt(mapper, connection, target):
    if target.id is not None:
        return

    target.id = Prompt.generate_id(target.prompt)


class Prompts(Model):
    prompts: list[Prompt]
    count: int


class Theme(Model, table=True):
    __tablename__ = "theme"
    id: str = Field(primary_key=True, default=None)
    theme: str = Field()
    active: str = Field()

    # TODO Theme needs a lifetime

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


class ReadingDevice(Model, table=True):
    __tablename__ = "reading_device"
    id: str = Field(primary_key=True)
    ip: str = Field()
    name: str = Field()
    color_support: str = Field()


class Queue(Model):
    id: str = Field(primary_key=True)


class Settings(Model):
    key: str = Field(primary_key=True)
    value: str = Field()
