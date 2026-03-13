from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_barras_equipo = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    tipo_equipo = Column(String(50), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(String(20), default="Fuera", nullable=False)

    usuario_registra_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_registra = relationship("Usuario", foreign_keys=[usuario_registra_id])

    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=True)
    estudiante = relationship("Estudiante", back_populates="equipos")

    movimientos = relationship("Movimiento", back_populates="equipo")
