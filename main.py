from typing import Annotated

import sqlalchemy
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import bcrypt
import models
from database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    email: text
    name: text
    password_hash: text


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    def row2dict(row):
        return {key: row[key] for key in row.keys()}
    try:
        # Construct the SQL query
        sql_query = text("SELECT * FROM users")
        # Execute the query
        results = db.execute(sql_query).fetchall()
        # Convert the results into a list of dictionaries
        users = [row2dict(row) for row in results]
        # Get the total number of users
        total = len(users)
        # Return the results
        return JSONResponse(content={"users": users, "total": total})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})

@app.post("/users")
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    # Hash the password
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    # Create the new user
    db_user = models.Users(email=user.email, name=user.name, password_hash=password_hash)

    try:
        # Add the new user to the database
        db.add(db_user)
        db.commit()
    except IntegrityError:
        # If the email already exists, rollback the transaction and return an error
        db.rollback()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={f"Duplicate e-mail: {user.email}"})

    # If the user was successfully added, return an empty response
    return {"message": "User created successfully"}


    # def row2dict(email, name):
    #     return {key: email[email, name] for key in email.keys()}
    # try:
    #     Construct the SQL query
        # sql_query = text("SELECT * FROM users")
        # Execute the query
        # results = db.execute(sql_query).fetchall()
        # Convert the results into a list of dictionaries
        # users = [row2dict(email=) for row in results]
        # Get the total number of users
        # total = len(users)
        # Return the results
        # return JSONResponse(content={"users": users, "total": total})
    # except Exception as e:
    #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})

