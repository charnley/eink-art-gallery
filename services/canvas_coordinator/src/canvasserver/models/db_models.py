import enum
import gzip
import io
import uuid
from hashlib import sha256

from PIL import Image as PilImage
from pydantic import model_serializer
from shared_constants import IMAGE_FORMAT, WaveshareDisplay
from sqlalchemy import event
from sqlmodel import Field, LargeBinary, Relationship
from sqlmodel import SQLModel as Model


def compress(s):
    if isinstance(s, str):
        s = s.encode()
    b = gzip.compress(s)
    return b


def decompress(b):
    s = gzip.decompress(b)
    return s


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


class Prompt(Model, table=True):

    __tablename__: str = "prompt"

    id: str = Field(primary_key=True, default=None)
    prompt: str = Field()
    image_model: str = Field()
    min_images: int = Field(default=6, nullable=False)
    display_model: WaveshareDisplay = Field(nullable=False)

    active: bool = Field(default=False)

    @staticmethod
    def generate_id(prompt_text: str, display_model: WaveshareDisplay) -> str:
        m = sha256()
        txt = prompt_text + " " + str(display_model)
        m.update(txt.encode())
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
        }

    def __str__(self) -> str:
        return f"Prompt(id='{str(self.id):20s}',active={str(self.active)}),display={self.display_model}"

    def __repr__(self) -> str:
        return str(self)


@event.listens_for(Prompt, "before_insert")
def ensure_id_in_prompt(mapper, connection, target):
    if target.id is not None:
        return

    target.id = Prompt.generate_id(target.prompt, target.display_model)


class FrameGroup(Model, table=True):

    __tablename__ = "frame_group"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    cron_schedule: str = Field(default="*/10 * * * *")

    default: bool = Field(
        default=False, nullable=False, description="Is this the default group for PullFrames?"
    )

    frames: list["Frame"] = Relationship(back_populates="group")

    def __str__(self):
        return f"FrameGroup(name={self.name}, cron={self.cron_schedule})"

    def __repr__(self):
        return str(self)


class FrameType(str, enum.Enum):
    PULL = "pull"
    PUSH = "push"


class Frame(Model, table=True):

    __tablename__ = "frame"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: FrameType = Field(nullable=False)
    model: WaveshareDisplay = Field(nullable=False)

    # PullFrames use MAC; PushFrames use IP/hostname
    mac: str | None = Field(default=None, unique=True)
    endpoint: str | None = Field(default=None, unique=True)

    group_id: str | None = Field(foreign_key="frame_group.id", nullable=True)
    group: FrameGroup | None = Relationship(back_populates="frames")

    def __str__(self):
        identifier = self.mac or self.endpoint
        return f"Frame(id={self.id}, type={self.type}, id_val={identifier}, group={self.group_id})"

    def __repr__(self):
        return str(self)

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "endpoint": "192.168.1.102:8080",
    #             },
    #             {
    #                 "mac": "00:1A:2B:3C:4D:5E",
    #                 "model": str(WaveshareDisplay.WaveShare13BlackWhite960x680)
    #             }
    #         ]
    #     }
    # }


class Settings(Model):
    key: str = Field(primary_key=True)
    value: str = Field()
