from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.database import Base

# Solo para Pylance/type checkers: evita el error "is not defined"
# en las relaciones sin crear importaciones circulares en ejecucion
if TYPE_CHECKING:
    from models.producto_model import Producto

# Tipos de movimiento
ENTRADA = "entrada"
SALIDA = "salida"


class MovimientoInventario(Base):
    """Registro de cada entrada o salida de unidades de un producto."""

    __tablename__ = "inventory_movement"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    tipo: Mapped[str] = mapped_column(String(10))  # "entrada" o "salida"
    cantidad: Mapped[int]
    fecha: Mapped[datetime] = mapped_column(default=datetime.now)
    motivo: Mapped[Optional[str]] = mapped_column(String(120))
    # Si la salida la provoco una venta, queda enlazada
    venta_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sale.id"))

    producto: Mapped["Producto"] = relationship()

    def __repr__(self) -> str:
        return f"MovimientoInventario(id={self.id!r}, producto_id={self.producto_id!r}, tipo={self.tipo!r}, cantidad={self.cantidad!r})"
