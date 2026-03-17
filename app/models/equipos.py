from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Equipo(Base):
    __tablename__ = "equipos"

    id                  = Column(BigInteger, primary_key=True, index=True)
    codigo_barras_equipo= Column(String(100), unique=True)       # nullable
    serial              = Column(String(150), unique=True)       # ← NUEVO
    nombre              = Column(String(150), nullable=False)
    descripcion         = Column(Text)
    tipo_equipo         = Column(String(100))
    fecha_registro      = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado              = Column(String(20), nullable=False, default="DISPONIBLE")
    # Valores válidos: 'DISPONIBLE' | 'INGRESADO' | 'RETIRADO'

    # FK: columna en BD se llama "usuario_registra"
    usuario_registra = Column(
        BigInteger,
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    registrado_por = relationship("Usuario", foreign_keys=[usuario_registra])

    estudiante_id = Column(
        BigInteger,
        ForeignKey("estudiantes.id"),
        nullable=False,         # ← NOT NULL en esquema real
        index=True
    )
    estudiante  = relationship("Estudiante", back_populates="equipos")
    movimientos = relationship("Movimiento", back_populates="equipo")

