from typing import Optional
from sqlalchemy.orm import Session
from app.models.roles import Rol


def get_rol_by_id(db: Session, rol_id: int) -> Optional[Rol]:
    return db.query(Rol).filter(Rol.id == rol_id).first()
