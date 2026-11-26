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

class CompraMovimiento(Base):
    __tablename__ = "purchase_movement"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    order_id : Mapped[int] = mapped_column(ForeignKey("sale.id"))
    payment_sequential : Mapped[int]
    payment_type : Mapped[str] = mapped_column(String(20))
    payment_installments : Mapped[int]
    payment_value : Mapped[float]

    venta : Mapped["Venta"] = relationship()


    def __repr__(self) -> str:
        return f"CompraMovimiento(id={self.id!r}, order_id={self.order_id!r}, payment_type={self.payment_type!r}, payment_value={self.payment_value!r})"
