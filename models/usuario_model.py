from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from models.database import Base

# Roles disponibles en el sistema
ROL_ADMIN = "administrador"
ROL_VENDEDOR = "vendedor"


class Usuario(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80))
    usuario: Mapped[str] = mapped_column(String(40), unique=True)
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    # Nunca se guarda la contrasena en texto plano, solo su hash bcrypt
    password_hash: Mapped[str] = mapped_column(String(60))
    rol: Mapped[str] = mapped_column(String(20), default=ROL_VENDEDOR)

    def es_admin(self) -> bool:
        return self.rol == ROL_ADMIN

    def __repr__(self) -> str:
        return f"Usuario(id={self.id!r}, usuario={self.usuario!r}, rol={self.rol!r})"
