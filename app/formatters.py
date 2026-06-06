from .types import Transaction


def format_transaction(
    tx: Transaction,
    template: str = "{date}\t{method}\t{code}\t{description}\t{category}\t{amount}",
    default_category: str = "",
    padding: bool = False,
) -> str:
    """Format a transaction as a string using the specified template and
    optional padding.
    """

    amount = f"{tx.get('amount'):.2f}"
    method = tx.get("method")
    category = tx.get("category") or default_category
    code = tx.get("code") or ""
    date = tx.get("date").strftime("%Y-%m-%d")
    description = tx.get("description")
    posting_date = tx.get("posting_date").strftime("%Y-%m-%d")

    return template.format(
        amount=amount if not padding else amount.ljust(10),
        method=method if not padding else method.ljust(10),
        category=category if not padding else category.ljust(30),
        code=code if not padding else code.ljust(23),
        date=date if not padding else date.ljust(10),
        description=description if not padding else description.ljust(90),
        posting_date=posting_date if not padding else posting_date.ljust(10),
    )
