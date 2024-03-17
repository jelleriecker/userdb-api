from sqlalchemy import Column, String
from database import Base


class Users(Base):
    __tablename__ = "users"

    email = Column(String, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)
    password_hash = Column(String)

