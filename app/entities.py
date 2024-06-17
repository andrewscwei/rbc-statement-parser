from datetime import datetime
from typing import TypedDict


class Transaction(TypedDict):
    amount: float
    category: str
    code: str | None
    date: datetime
    description: str
    posting_date: datetime
