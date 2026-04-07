from sqlalchemy import Column, BigInteger, String, Text
from app.db.base import Base

class Rol(Base):
    __tablename__ = "roles"

    id          = Column(BigInteger, primary_key=True, index=True)
    nombre      = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
