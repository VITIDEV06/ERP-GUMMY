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
    from models.venta_model import Venta
    from models.producto_model import Producto


class DetalleVenta(Base):
    """Una linea de una venta: que producto, cuantas unidades y a que precio.

    (Antes se llamaba Compra / tabla purchase: representaba los items de cada pedido.)
    """

    __tablename__ = "sale_detail"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("sale.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    cantidad: Mapped[int]
    # Se guarda el precio del momento de la venta (el del producto puede cambiar)
    precio_unitario: Mapped[float]
    subtotal: Mapped[float]

    venta: Mapped["Venta"] = relationship(back_populates="detalles")
    producto: Mapped["Producto"] = relationship()

    def __repr__(self) -> str:
        return f"DetalleVenta(id={self.id!r}, venta_id={self.venta_id!r}, producto_id={self.producto_id!r}, cantidad={self.cantidad!r})"
