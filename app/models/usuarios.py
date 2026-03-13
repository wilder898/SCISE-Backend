from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    area = Column(String(100))
    estado = Column(Boolean, default=True)

    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    rol = relationship("Rol")
