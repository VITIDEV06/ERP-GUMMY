from datetime import datetime
from typing import List
from typing import TYPE_CHECKING
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer
from models.database import Base

# Solo para Pylance/type checkers: evita el error "is not defined"
# en las relaciones sin crear importaciones circulares en ejecucion
if TYPE_CHECKING:
    from models.venta_model import Venta
    from models.producto_model import Producto
    from models.vendedor_model import Vendedor

class Compra(Base):
    __tablename__ = "purchase"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    order_id : Mapped[int] = mapped_column(ForeignKey("sale.id"))
    order_item_id : Mapped[int]
    product_id : Mapped[int] = mapped_column(ForeignKey("product.id"))
    seller_id : Mapped[int] = mapped_column(ForeignKey("seller.id"))
    shipping_limit_date : Mapped[datetime]
    price : Mapped[float]
    freight_value : Mapped[float]

    venta : Mapped["Venta"] = relationship()
    producto : Mapped["Producto"] = relationship()
    vendedor : Mapped["Vendedor"] = relationship()


    def __repr__(self) -> str:
        return f"Compra(id={self.id!r}, order_id={self.order_id!r}, order_item_id={self.order_item_id!r}, product_id={self.product_id!r}, price={self.price!r})"
