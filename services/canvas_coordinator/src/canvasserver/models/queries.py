from canvasserver.models.db_models import Frame, FrameGroup
from sqlmodel import Session


def get_pullframe_group(db: Session, mac: str | None):

    # Try registered frame first
    frame = db.query(Frame).filter_by(mac=mac).first() if mac else None
    if frame is not None and frame.group:
        return frame.group

    # Otherwise, return the default PullFrame group
    return db.query(FrameGroup).filter_by(default=True).first()
