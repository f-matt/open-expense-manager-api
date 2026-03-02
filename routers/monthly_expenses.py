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

from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlmodel import Session, select, desc

from config.auth import oauth2_scheme
from config.db import get_engine
from models.monthly_expenses import MonthlyExpenses
from models.expense import Expense

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()
engine = get_engine()

@router.post("/")
async def insert_monthly_expenses(monthly_expenses: MonthlyExpenses):
    with Session(engine) as session:
        try:
            session.add(monthly_expenses)

            for e in monthly_expenses.expenses:
                e.monthly_expenses_id = monthly_expenses.id
                session.add(monthly_expenses)

            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error inserting expense data.")

@router.patch("/")
async def update_monthly_expenses(monthly_expenses: MonthlyExpenses):
    if not monthly_expenses:
        raise HTTPException(status_code=422, detail="Must provide monthly expenses data.")

    if not monthly_expenses.id:
        raise HTTPException(status_code=422, detail="Monthly expenses id not found.")

    with Session(engine) as session:
        try:
            statement = select(MonthlyExpenses).where(MonthlyExpenses.id == monthly_expenses.id)
            m = session.exec(statement).one_or_none()

            if not m:
                raise HTTPException(status_code=422, detail="No monthly expenses found with the provided id.")

            m.reference_date = monthly_expenses.reference_date
            m.processing_date = monthly_expenses.processing_date
            session.merge(m)

            statement = select(Expense).where(Expense.monthly_expenses_id == m.id)
            remaining_expenses = list(session.exec(statement).all())

            for e in monthly_expenses.expenses:
                e.monthly_expenses_id = m.id
                if not e.id:
                    session.add(e)
                else:
                    session.merge(e)

                for r in remaining_expenses:
                    if r.id == e.id:
                        remaining_expenses.remove(r)

            for r in remaining_expenses:
                session.delete(r)

            session.commit()
        except HTTPException as e:
            session.rollback()
            raise e
        except Exception:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error updating monthly expense data.")

@router.get("/")
async def get_monthly_expenses(token: Annotated[str, Depends(oauth2_scheme)]):
    with Session(engine) as session:
        try:
            statement = select(MonthlyExpenses).order_by(desc(MonthlyExpenses.reference_date))
            results = session.exec(statement)

            return results.all()
        except Exception as e:
            logger.exception("Error getting monthly expenses", e)
            raise HTTPException(status_code=400, detail="Error getting monthly expenses.")
