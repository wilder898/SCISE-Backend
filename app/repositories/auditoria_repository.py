from datetime import datetime
from sqlalchemy.orm import Session
from app.models.auditoria import Auditoria


def create_auditoria(
    db: Session,
    usuario_id: int,
    evento: str,
    tipo_auditoria: str,
    tabla_id: int,
    valor_anterior: str,
    valor_nuevo: str,
    url: str,
) -> None:
    """Registra una entrada de auditoría. No hace commit — se espera que el llamador lo gestione."""
    db.add(
        Auditoria(
            usuario_id=usuario_id,
            evento=evento,
            tipo_auditoria=tipo_auditoria,
            tabla_id=tabla_id,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            url=url,
            fecha_novedad=datetime.utcnow(),
        )
    )
