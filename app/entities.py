from datetime import datetime
from typing import Optional, TypedDict


class Transaction(TypedDict):
    date: datetime
    method: str
    description: str
    amount: float
    category: Optional[str]
    code: Optional[str]
    posting_date: datetime
