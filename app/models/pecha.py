from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Pecha(Base):
    id = Column(Integer, primary_key=True, index=True)
    img = Column(String, index=True, nullable=True)
    title = Column(String, index=True)
    subtitle = Column(String, index=True, nullable=True)
    author = Column(String, index=True, nullable=True)
    volume = Column(String, index=True, nullable=True)
    collection_title = Column(String, index=True, nullable=True)
    publisher = Column(String, index=True, nullable=True)
    source_id = Column(String, index=True, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="pechas")
    collaborators = relationship("User", back_populates="pechas")
