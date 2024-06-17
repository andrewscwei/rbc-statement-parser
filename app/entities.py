from datetime import datetime
from typing import Dict, List, Optional, TypedDict


class Config(TypedDict, total=False):
    format: Optional[str]
    categories: Optional[Dict[str, List[str]]]
    excludes: Optional[List[str]]


class Transaction(TypedDict, total=False):
    date: datetime
    method: str
    description: str
    amount: float
    category: Optional[str]
    code: Optional[str]
    posting_date: datetime
