import re

max_col_widths = {
  "date": 6,
  "code": 23,
  "desc": 40,
  "value": 15,
}

exclude_line_regexes = [
  r'PAYMENT - THANK YOU',
]

categories = {
  "Alcohol": [],
  "Transportation/Gas": [],
  "Transportation/Insurance": [],
  "Transportation/Loans": [],
  "Transportation/Maintenance": [],
  "Transportation/Parking": [],
  "Transportation/Penalties": [],
  "Bank/Charges": [
    r''
  ],
  "Bank/Interests": [],
  "Business/Admin": [],
  "Coffee": [],
  "Clothing": [],
  "Commute/Public Transit": [],
  "Digital/Recreation": [],
  "Digital/Resources": [],
  "Digital/Utilities": [],
  "Electronics/Accessories": [],
  "Electronics/Devices": [],
  "Electronics/Recreation": [],
  "Events/Business": [],
  "Events/Recreation": [],
  "Food": [],
  "Groceries": [],
  "Hobbies": [],
  "Household/Bills": [],
  "Household/Enhancements": [],
  "Income": [],
  "Investments/Cryptocurrency": [],
  "Investments/RRSP": [],
  "Medical/Drugs": [],
  "Medical/Insurance": [],
  "Medical/Practitioners": [],
  "Office Supplies": [],
  "Telecom/Home": [],
  "Telecom/Mobile": [],
  "Travel": [],
  "Others": [],
}
