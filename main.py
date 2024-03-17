from typing import Annotated

from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import bcrypt
import models
from database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    email: str
    name: str
    password_hash: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/users")
async def get_users(query: str, limit: int, db: Session = Depends(get_db)):
    # Construct the SQL query
    sql_query = text("SELECT * FROM users WHERE name LIKE :name LIMIT :limit")
    # Execute the query
    results = db.execute(sql_query, {"name": f"{query}%", "limit": limit}).fetchall()
    # Convert the results into a list of dictionaries
    users = [dict(row) for row in results]
    # Get the total number of matched records
    total = len(users)
    # Return the results
    return {"users": users, "total": total}


@app.post("/users", status_code=status.HTTP_202_ACCEPTED)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    # Create the new user
    db_user = models.Users(email=user.email, name=user.name, hashed_password=hashed_password)

    try:
        # Add the new user to the database
        db.add(db_user)
        db.commit()
    except IntegrityError:
        # If the email already exists, rollback the transaction and return an error
        db.rollback()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": f"Duplicate e-mail: {user.email}"})

    # If the user was successfully added, return an empty response
    return {}
