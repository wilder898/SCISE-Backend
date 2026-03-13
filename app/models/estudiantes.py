from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    codigo_barras = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    ficha = Column(String(20), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    usuario_crea_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_crea = relationship("Usuario", foreign_keys=[usuario_crea_id])

    equipos = relationship("Equipo", back_populates="estudiante")
    movimientos = relationship("Movimiento", back_populates="estudiante")
