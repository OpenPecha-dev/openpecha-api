from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import update

from app.crud.base import CRUDBase
from app.models.pecha import Pecha
from app.schemas.pecha import PechaCreate, PechaUpdate


class CRUDPecha(CRUDBase[Pecha, PechaCreate, PechaUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: PechaCreate, owner_id: int
    ) -> Pecha:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Pecha]:
        return (
            db.query(self.model)
            .filter(Pecha.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, db: Session, *, db_obj: Pecha, obj_in: PechaUpdate, owner_id: int
    ) -> Pecha:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


pecha = CRUDPecha(Pecha)
