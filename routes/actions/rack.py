from sqlalchemy.orm import Session

from models.models import Rack


def get_rack_by_id(db: Session, id: str) -> Rack | None:
    """Retrieves a Rack object with the specified ID from the database.

    Args:
        db: A SQLAlchemy Session object.
        id: The ID of the rack to retrieve.

    Returns:
        The Rack object with the given ID, or None if not found.
    """

    rack = db.query(Rack).filter(Rack.rack_id == id).first()

    return rack
