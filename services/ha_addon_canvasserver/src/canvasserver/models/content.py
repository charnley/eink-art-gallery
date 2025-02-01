import gzip
import io
import uuid
from hashlib import sha256

from PIL import Image
from sqlalchemy import event
from sqlmodel import Field, LargeBinary
from sqlmodel import SQLModel as Model
from sqlmodel import TypeDecorator


def compress(s):
    if type(s) == str:
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
        image.save(output, format="PNG")
        hex_data = output.getvalue()
        return hex_data

    @staticmethod
    def load_image(hex_data):
        image = Image.open(io.BytesIO(hex_data))
        return image

    def process_bind_param(self, value, dialect):
        return compress(self.save_image(value))

    def process_result_value(self, value, dialect):
        return self.load_image(decompress(value))


class Image(Model, table=True):
    __tablename__ = "image"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    prompt: str = Field(foreign_key="prompt.id", nullable=False, ondelete="CASCADE")
    image_data: bytes = Field(sa_column=LargeBinary)

    @property
    def image(self) -> Image.Image:
        return Image.open(io.BytesIO(self.image_data))

    @image.setter
    def image(self, image: Image.Image) -> None:
        output = io.BytesIO()
        image.save(output, format="PNG")
        hex_data = output.getvalue()
        self.image_data = hex_data


class Images(Model):
    images: list[Image]
    count: int


class Prompt(Model, table=True):
    __tablename__ = "prompt"
    id: str = Field(primary_key=True, default=None)
    prompt: str = Field()
    model: str = Field()

    @staticmethod
    def generate_id(prompt_text: str) -> str:
        m = sha256()
        m.update(prompt_text.encode())
        return m.hexdigest()


@event.listens_for(Prompt, "before_insert")
def ensure_id_in_prompt(mapper, connection, target):
    if not target.id is None:
        return

    target.id = Prompt.generate_id(target.prompt)


class Prompts(Model):
    prompts: list[Prompt]
    count: int


class ReadingDevice(Model, table=True):
    __tablename__ = "reading_device"
    id: str = Field(primary_key=True)
    ip: str = Field()
    name: str = Field()


class Queue(Model):
    id: str = Field(primary_key=True)
