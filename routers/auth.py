# The MIT License
#
# Copyright (c) 2025-2025 Fernando Mattioli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import datetime
from typing import Optional, Annotated

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, select

from config.config import get_config
from db.config import get_engine

import jwt

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str

class Credentials(BaseModel):
    username: str
    password: str

router = APIRouter()
engine = get_engine()

config = get_config()
jwt_secret = config["jwt_secret"]

@router.post("/login")
async def login(credentials: Credentials):
    with Session(engine) as session:
        try:
            statement = select(User).where(User.username == credentials.username)
            user = session.exec(statement).one_or_none()

            if not user:
                raise HTTPException(status_code=401, detail="Invalid username/password.")

            ph = PasswordHasher()
            if ph.verify(user.password, credentials.password):
                access_exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5)
                refresh_exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
                access_jwt = jwt.encode({"username": credentials.username, "exp": access_exp}, jwt_secret,
                                        algorithm="HS256")
                refresh_jwt = jwt.encode({"username": credentials.username, "exp": refresh_exp}, jwt_secret,
                                         algorithm="HS256")

                return {"access": access_jwt, "refresh": refresh_jwt}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e

            if isinstance(e, VerifyMismatchError):
                raise HTTPException(status_code=401, detail="Invalid username/password.")

    raise HTTPException(status_code=401, detail="Error authenticating user.")

@router.post("/validate")
async def validate(authorization: Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authentication header.")

    token = authorization.split()[1]
    try:
        jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return { "valid": True }
    except:
        raise HTTPException(status_code=401, detail="Invalid token.")
