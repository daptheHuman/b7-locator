from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import models
from schemas import user_schemas


def update_user(
    db: Session,
    id: int,
    updated_user: user_schemas.UserUpdate,
):
    # Retrieve the user from the database
    existing_user = db.query(models.User).filter(models.User.id == id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert the updated_user to a dictionary and filter out None values
    update_data = updated_user.model_dump(exclude_unset=True)

    # Update user attributes
    existing_user.update(update_data)

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated sample
    return existing_user.first()


def delete_user(
    db: Session,
    id: int,
):
    # Retrieve the user from the database
    existing_user = db.query(models.User).filter(models.User.id == id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(existing_user)

    # Commit the transaction to save the changes
    db.commit()

    # Return a message indicating successful deletion
    return {"message": "User deleted successfully"}
