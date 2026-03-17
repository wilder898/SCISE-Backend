from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id            = Column(BigInteger, primary_key=True, index=True)
    codigo_barras = Column(String(100), unique=True)        # nullable, asignado luego
    documento     = Column(String(50),  unique=True, nullable=False)   # ← NUEVO
    nombre        = Column(String(150), nullable=False)
    ficha         = Column(String(100))
    celular       = Column(String(20))                      # ← NUEVO
    estado        = Column(String(20),  nullable=False, default="ACTIVO")
    # Valores válidos: 'ACTIVO' | 'INACTIVO'

    # FK: la columna en BD se llama "usuario_crea", no "usuario_crea_id"
    usuario_crea = Column(
        BigInteger,
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    creado_por = relationship("Usuario", foreign_keys=[usuario_crea])

    equipos      = relationship("Equipo",      back_populates="estudiante")
    movimientos  = relationship("Movimiento",  back_populates="estudiante")