from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer
from models.database import Base

class Producto(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    product_category_name: Mapped[Optional[str]] = mapped_column(String(50))
    product_weight_g : Mapped[float]
    product_length_cm : Mapped[float]
    product_height_cm : Mapped[float]
    product_width_cm : Mapped[float]
    price : Mapped[float]


    def __repr__(self) -> str:
        return f"Producto(id={self.id!r}, product_category_name={self.product_category_name!r}, price={self.price!r})"
