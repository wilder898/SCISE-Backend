from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Movimiento(Base):
    __tablename__ = "movimientos"

    id              = Column(BigInteger, primary_key=True, index=True)
    tipo_movimiento = Column(String(20), nullable=False)
    # Valores válidos: 'INGRESO' | 'SALIDA'
    fecha_registro  = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario_id   = Column(BigInteger, ForeignKey("usuarios.id"),    nullable=False, index=True)
    equipo_id    = Column(BigInteger, ForeignKey("equipos.id"),     nullable=False, index=True)
    estudiante_id= Column(BigInteger, ForeignKey("estudiantes.id"), nullable=False, index=True)

    usuario    = relationship("Usuario",    foreign_keys=[usuario_id])
    equipo     = relationship("Equipo",     back_populates="movimientos")
    estudiante = relationship("Estudiante", back_populates="movimientos")

