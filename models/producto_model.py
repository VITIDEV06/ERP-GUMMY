from typing import Optional
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from models.database import Base


class Producto(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[Optional[str]] = mapped_column(String(50))
    precio: Mapped[float]
    # Cantidad disponible en inventario
    stock: Mapped[int] = mapped_column(Integer, default=0)
    # Por debajo de este valor el producto se considera "bajo inventario"
    stock_minimo: Mapped[int] = mapped_column(Integer, default=5)
    # Codigo original del CSV de Olist (solo para los datos de demostracion)
    codigo_origen: Mapped[Optional[str]] = mapped_column(String(32))

    def bajo_stock(self) -> bool:
        return self.stock <= self.stock_minimo

    def __repr__(self) -> str:
        return f"Producto(id={self.id!r}, nombre={self.nombre!r}, precio={self.precio!r}, stock={self.stock!r})"
