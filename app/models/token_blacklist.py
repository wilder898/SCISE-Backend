from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id               = Column(BigInteger, primary_key=True, index=True)
    jti              = Column(String(255), unique=True, nullable=False, index=True)
    fecha_revocacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    usuario    = relationship("Usuario", foreign_keys=[usuario_id])
