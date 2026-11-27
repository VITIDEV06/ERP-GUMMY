from typing import Optional
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from models.database import Base


class Cliente(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    telefono: Mapped[Optional[str]] = mapped_column(String(20))
    correo: Mapped[Optional[str]] = mapped_column(String(120))
    ciudad: Mapped[Optional[str]] = mapped_column(String(50))
    estado: Mapped[Optional[str]] = mapped_column(String(50))
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(5))
    # Codigo original del CSV de Olist (solo para los datos de demostracion)
    codigo_origen: Mapped[Optional[str]] = mapped_column(String(32))

    def __repr__(self) -> str:
        return f"Cliente(id={self.id!r}, nombre={self.nombre!r}, ciudad={self.ciudad!r})"
