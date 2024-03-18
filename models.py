from sqlalchemy import Column, String
from database import Base


class Users(Base):
    # noinspection SpellCheckingInspection
    __tablename__ = "users"

    email = Column(String, unique=True, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
