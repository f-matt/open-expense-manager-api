#!/bin/python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field, Session, select

from argon2 import PasswordHasher

DATABASE_URL = "postgresql://oem:123456@localhost/oem"
engine = create_engine(DATABASE_URL, echo=True)

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str


class Credentials(BaseModel):
    username: str
    password: str

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.post("/api/login")
async def login(credentials: Credentials):
    with Session(engine) as session:
        try:
            statement = select(User).where(User.username == credentials.username)
            results = session.exec(statement)

            if not results:
                raise HTTPException(status_code=401, detail="Invalid username/password.")

            users = results.all()
            if len(users) != 1:
                raise HTTPException(status_code=401, detail="Invalid username/password.")

            ph = PasswordHasher()
            if ph.verify(users[0].password, credentials.password):
                return {"message": "ok"}
        except Exception as e:
            print(e)

    raise HTTPException(status_code=401, detail="Invalid username/password.")
