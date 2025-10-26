from canvasserver.models.db_models import Frame, FrameGroup
from shared_constants import FrameType, WaveshareDisplay
from sqlmodel import Session


def get_frame_group(db: Session, mac: str | None):

    # Try registered frame first
    frame = db.query(Frame).filter_by(mac=mac).first() if mac else None
    if frame is not None and frame.group:
        return frame.group

    # Otherwise, return the default PullFrame group


def get_default_group(session):
    return session.query(FrameGroup).filter_by(default=True).first()


def register_frame_default_group(session: Session, frame: Frame) -> FrameGroup | None:

    group = session.query(FrameGroup).filter_by(default=True).first()

    if group is None:
        return None

    frame.group_id = group.id

    return group


def register_new_frame(session: Session, mac: str, display_model: WaveshareDisplay) -> Frame:

    default_group = get_default_group(session)
    group_id = default_group.id if default_group is not None else None

    # Default
    frame = Frame(
        mac=mac,
        model=display_model,
        group_id=group_id,
        type=FrameType.PULL,
    )

    session.add(frame)

    return frame
