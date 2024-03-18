import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker


load_dotenv()

DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users(db: Session, name: str, limit: int) -> list[dict[str, str]]:
    # Construct the SQL query
    results = db.execute(
        DatabaseUser.__table__.select().where(DatabaseUser.name.like(name)).limit(limit)).fetchall()
    # Convert the results to a list of dictionaries
    users = [row._asdict() for row in results]

    return users


def create_user(db: Session, name: str, email: str, password_hash: str) -> None:
    # Create the new user
    db_user = DatabaseUser(email=email, name=name, password_hash=password_hash)

    try:
        # Add the new user to the database
        db.add(db_user)
        db.commit()
    except IntegrityError:
        # If the email already exists, rollback the transaction and return an error
        db.rollback()

        raise Exception(f"Duplicate e-mail: {email}")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DatabaseUser(Base):
    # noinspection SpellCheckingInspection
    __tablename__ = "users"

    email = Column(Text, unique=True, primary_key=True, index=True, nullable=False)
    name = Column(Text, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)
