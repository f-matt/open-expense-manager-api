"""init db

Revision ID: 788eddb90f01
Revises: 
Create Date: 2026-03-02 12:05:36.127875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '788eddb90f01'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
CREATE TABLE users (
    id SERIAL,
    username VARCHAR (50) NOT NULL,
    password VARCHAR (256) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO users (username, password)
VALUES ('admin', '$argon2id$v=19$m=65536,t=3,p=4$M1eldHErkjbAaxNed8vbOQ$iXMKR6QzkAae5vBUgOMoOdvUV4BrpQ+mzesNwNS+l1g');

CREATE TABLE recurring_expenses (
    id SERIAL,
    name VARCHAR (50) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    value DECIMAL (8, 2),
    PRIMARY KEY (id)
);

CREATE TABLE monthly_expenses (
    id SERIAL,
    reference_date DATE NOT NULL,
    processing_date DATE NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE expenses (
    id SERIAL,
    value DECIMAL (8, 2) NOT NULL,
    recurring_expense_id INTEGER NOT NULL,
    monthly_expense_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (recurring_expense_id) REFERENCES recurring_expenses (id),
    FOREIGN KEY (monthly_expense_id) REFERENCES monthly_expenses (id)
);
""")

def downgrade() -> None:
    op.execute("""
DROP TABLE expenses;
DROP TABLE monthly_expenses;
DROP TABLE recurring_expenses;
DROP TABLE users;
""")
