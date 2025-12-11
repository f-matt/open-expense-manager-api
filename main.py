#!/bin/python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str

app = FastAPI()

@app.post("/api/login")
async def login(credentials: Credentials):
    if credentials.username == "admin" and credentials.password == "123":
        return {"message" : "ok"}

    raise HTTPException(status_code=401, detail="Invalid username/password.")
