from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Auditoria(Base):
    __tablename__ = "auditoria"

    id             = Column(BigInteger, primary_key=True, index=True)
    evento         = Column(String(150), nullable=False)
    tipo_auditoria = Column(String(100))
    tabla_id       = Column(BigInteger)
    valor_anterior = Column(Text)
    valor_nuevo    = Column(Text)
    url            = Column(Text)
    fecha_novedad  = Column(DateTime, nullable=False, default=datetime.utcnow)

    # FK: usuario_id referencia a usuarios.id
    usuario_id = Column(
        BigInteger,
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

