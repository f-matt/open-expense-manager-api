#!/bin/python
import configparser
import jwt

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field, Session, select

from argon2 import PasswordHasher

config = configparser.ConfigParser()
config.read(".env")

DATABASE_URL = config.get("OEM", "DATABASE_URL")
JWT_SECRET = config.get("OEM", "JWT_SECRET")

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
                access_exp = datetime.now() + timedelta(minutes=5)
                refresh_exp = datetime.now() + timedelta(minutes=30)
                access_jwt = jwt.encode({"username": credentials.username, "exp": access_exp}, JWT_SECRET,
                                         algorithm="HS256")
                refresh_jwt = jwt.encode({"username": credentials.username, "exp": refresh_exp}, JWT_SECRET,
                                         algorithm="HS256")
                return {"access": access_jwt, "refresh": refresh_jwt}
        except Exception as e:
            print(e)

    raise HTTPException(status_code=401, detail="Invalid username/password.")
