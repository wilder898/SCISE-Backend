from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.base import Base

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(100), nullable=False)
    evento = Column(String(100), nullable=False)
    tipo_auditoria = Column(String(50), nullable=False)
    tabla_id = Column(Integer, nullable=True)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    fecha_novedad = Column(DateTime, default=datetime.utcnow, nullable=False)
    descripcion = Column(Text, nullable=True)
