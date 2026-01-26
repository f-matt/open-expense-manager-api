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
import logging

from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, Field, Session, select

from db.config import get_engine

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    value: Optional[float]
    active: bool

router = APIRouter()
engine = get_engine()

@router.post("/expenses")
async def insert_expense(expense: Expense):
    with Session(engine) as session:
        try:
            if expense.value:
                print ("Has value")
                new_expense = Expense(name=expense.name, value=expense.value, active=expense.active)
            else:
                print ("No value")
                new_expense = Expense(name=expense.name, active=expense.active)

            session.add(new_expense)
            session.commit()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error inserting expense data.")

@router.get("/expenses")
async def get_expenses():
    with Session(engine) as session:
        try:
            statement = select(Expense)
            results = session.exec(statement)
            return results.all()
        except Exception as e:
            logger.exception("Error getting expenses", e)
            raise HTTPException(status_code=400, detail="Error getting expenses.")
