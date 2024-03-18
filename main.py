from typing import Annotated

import bcrypt
import uvicorn
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

import database
from database import get_db

app = FastAPI()


class RequestUser(BaseModel):
    email: str
    name: str
    password: str


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/users")
async def get_users(query: str = "%", limit: int = 10, db: Session = Depends(get_db)):
    try:
        users = database.get_users(db, query, limit)

        # Get the total number of users
        total = len(users)
        # Return the results
        return JSONResponse(content={"users": users, "total": total})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)})

@app.post("/users")
async def create_user(user: RequestUser, db: Session = Depends(get_db)):
    # Hash the password
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    try:
        database.create_user(db, name=user.name, email=user.email, password_hash=password_hash)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={str(e)})

    # If the user was successfully added, return an empty response
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
