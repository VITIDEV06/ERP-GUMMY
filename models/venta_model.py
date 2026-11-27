from datetime import datetime
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.database import Base

# Solo para Pylance/type checkers: evita el error "is not defined"
# en las relaciones sin crear importaciones circulares en ejecucion
if TYPE_CHECKING:
    from models.cliente_model import Cliente
    from models.usuario_model import Usuario
    from models.detalle_venta_model import DetalleVenta


class Venta(Base):
    """Encabezado de una venta. Los productos vendidos estan en DetalleVenta."""

    __tablename__ = "sale"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(default=datetime.now)
    # El cliente es opcional: una venta de mostrador puede no tener cliente
    cliente_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))
    total: Mapped[float] = mapped_column(default=0.0)

    cliente: Mapped[Optional["Cliente"]] = relationship()
    usuario: Mapped[Optional["Usuario"]] = relationship()
    detalles: Mapped[List["DetalleVenta"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Venta(id={self.id!r}, fecha={self.fecha!r}, total={self.total!r})"
