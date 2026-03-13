from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_movimiento = Column(String(20), nullable=False)
    # Valores posibles: "INGRESO" | "SALIDA"
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    equipo = relationship("Equipo", back_populates="movimientos")

    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    estudiante = relationship("Estudiante", back_populates="movimientos")
