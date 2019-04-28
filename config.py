import re
from typing import Dict, List

max_col_widths: Dict[str, int] = {
  "date": 6,
  "code": 23,
  "desc": 40,
  "value": 15,
}

exclude_line_regexes: List[str] = [
  r'PAYMENT - THANK YOU',
]
