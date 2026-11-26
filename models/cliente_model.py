from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer
from models.database import Base

class Cliente(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    customer_unique_id : Mapped[str] = mapped_column(String(32))
    customer_zip_code_prefix : Mapped[str] = mapped_column(String(5))
    customer_city : Mapped[str] = mapped_column(String(50))
    customer_state : Mapped[str] = mapped_column(String(2))


    def __repr__(self) -> str:
        return f"Cliente(id={self.id!r}, customer_city={self.customer_city!r}, customer_state={self.customer_state!r})"
