from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Pecha(Base):
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=True)
    img = Column(String, index=True, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="pechas")
    collaborators = relationship("User", back_populates="pechas")
