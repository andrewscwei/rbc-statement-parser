from datetime import datetime
from typing import Optional, TypedDict


class Transaction(TypedDict):
    amount: float
    category: str
    code: Optional[str]
    date: datetime
    description: str
    posting_date: Optional[datetime]
