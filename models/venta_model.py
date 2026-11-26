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
    from models.cliente_model import Cliente
    from models.producto_model import Producto

class Venta(Base):
    __tablename__ = "sale"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    customer_id : Mapped[int] = mapped_column(ForeignKey("customer.id"))
    product_id : Mapped[int] = mapped_column(ForeignKey("product.id"))
    order_status : Mapped[str] = mapped_column(String(20))
    order_purchase_timestamp : Mapped[datetime]
    order_approved_at : Mapped[Optional[datetime]]
    order_delivered_carrier_date : Mapped[Optional[datetime]]
    order_delivered_customer_date : Mapped[Optional[datetime]]
    order_estimated_delivery_date : Mapped[datetime]
    frequency_in_items : Mapped[int]
    quantity : Mapped[int]

    cliente : Mapped["Cliente"] = relationship()
    producto : Mapped["Producto"] = relationship()


    def __repr__(self) -> str:
        return f"Venta(id={self.id!r}, customer_id={self.customer_id!r}, product_id={self.product_id!r}, quantity={self.quantity!r}, order_status={self.order_status!r})"
