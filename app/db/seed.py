from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.roles import Rol
from app.models.usuarios import Usuario
from app.core.security import hash_password
from app.core.config import settings

def seed_database():
    db: Session = SessionLocal()
    try:
        roles_data = [
            {"nombre": "Administrador", "descripcion": "Acceso completo al sistema"},
            {"nombre": "Seguridad",     "descripcion": "Registro de movimientos"},
            {"nombre": "Aprendiz",      "descripcion": "Consulta de equipos propios"},
            {"nombre": "Instructor",    "descripcion": "Consulta y validación"},
        ]
        for rd in roles_data:
            if not db.query(Rol).filter(Rol.nombre == rd["nombre"]).first():
                db.add(Rol(**rd))
        db.commit()

        rol_admin = db.query(Rol).filter(Rol.nombre == "Administrador").first()
        if not db.query(Usuario).filter(Usuario.correo == settings.admin_correo).first():
            db.add(Usuario(
                documento=settings.admin_documento,
                nombre=settings.admin_nombre,
                correo=settings.admin_correo,
                contrasena=hash_password(settings.admin_password),  # ← contrasena
                rol_id=rol_admin.id,
                estado="ACTIVO"   # ← STRING, no True
            ))
            db.commit()
            print("✅ Administrador creado")
        else:
            print("ℹ️  Administrador ya existe")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
