from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id         = Column(BigInteger, primary_key=True, index=True)
    documento  = Column(String(50),  unique=True,  nullable=False)
    nombre     = Column(String(150), nullable=False)
    correo     = Column(String(150), unique=True)
    contrasena = Column(Text, nullable=False)          # ← TEXT, no contrasena_hash
    area       = Column(String(100))
    estado     = Column(String(20),  nullable=False, default="ACTIVO")
    # Valores válidos: 'ACTIVO' | 'INACTIVO'  (CHECK en BD)

    rol_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False, index=True)
    rol    = relationship("Rol")
