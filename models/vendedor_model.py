from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer
from models.database import Base

class Vendedor(Base):
    __tablename__ = "seller"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    seller_zip_code_prefix : Mapped[str] = mapped_column(String(5))
    seller_city : Mapped[str] = mapped_column(String(50))
    seller_state : Mapped[str] = mapped_column(String(2))


    def __repr__(self) -> str:
        return f"Vendedor(id={self.id!r}, seller_city={self.seller_city!r}, seller_state={self.seller_state!r})"
