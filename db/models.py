from uuid import uuid4, UUID

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

##############################
# BLOCK WITH DATABASE MODELS #
##############################

class Base(DeclarativeBase):
    pass



class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    password: Mapped[str] = mapped_column(nullable=False)
