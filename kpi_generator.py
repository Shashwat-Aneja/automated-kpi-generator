import math
import sys

import pandas as pd


REQUIRED_COLUMNS = {"date", "amount", "type"}
SUPPORTED_TYPES = {"revenue", "expense"}


def validate_transactions(df):
    """Return a validated copy with normalized transaction types and numeric amounts."""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("CSV missing required columns: " + ", ".join(sorted(missing)))
    if df.empty:
        raise ValueError("CSV contains no transaction rows.")

    cleaned = df.copy()
    cleaned["type"] = cleaned["type"].astype("string").str.strip().str.lower()
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    parsed_dates = pd.to_datetime(cleaned["date"], errors="coerce")
    if parsed_dates.isna().any():
        raise ValueError("Transaction dates must be valid dates.")

    if cleaned["type"].isna().any() or (cleaned["type"] == "").any():
        raise ValueError("Transaction type cannot be empty.")
    unsupported = sorted(set(cleaned["type"].dropna()) - SUPPORTED_TYPES)
    if unsupported:
        raise ValueError("Unsupported transaction type(s): " + ", ".join(unsupported))
    if cleaned["amount"].isna().any():
        raise ValueError("Transaction amounts must be numeric.")
    if not cleaned["amount"].map(lambda amount: math.isfinite(float(amount))).all():
        raise ValueError("Transaction amounts must be finite numbers.")
    if cleaned["date"].isna().any() or (cleaned["date"].astype("string").str.strip() == "").any():
        raise ValueError("Transaction dates cannot be empty.")

    return cleaned


def calculate_kpis(df):
    """Calculate KPIs, print a human-readable report, and return reusable metrics."""
    df = validate_transactions(df)
    revenue = df[df["type"] == "revenue"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    profit = revenue - expenses
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0
    transaction_dates = pd.to_datetime(df["date"])

    summary = {
        "total_revenue": float(revenue),
        "total_expenses": float(expenses),
        "profit": float(profit),
        "profit_margin": float(profit_margin),
        "expense_ratio": float(expense_ratio),
        "transaction_count": int(len(df)),
        "period_start": transaction_dates.min().date().isoformat(),
        "period_end": transaction_dates.max().date().isoformat(),
    }

    print("\n===== KPI Report =====")
    print(f"Total Revenue      : ₹{revenue}")
    print(f"Total Expenses     : ₹{expenses}")
    print(f"Profit             : ₹{profit}")
    print(f"Profit Margin      : {profit_margin:.2f}%")
    print(f"Expense Ratio      : {expense_ratio:.2f}%")
    print(f"Transactions       : {len(df)}")
    print(f"Reporting Period   : {summary['period_start']} to {summary['period_end']}")
    print("Growth Rate        : N/A (single period)")
    print("======================\n")
    return summary


def main():
    if len(sys.argv) != 2:
        print("Usage: python kpi_generator.py <csv_file>")
        return

    csv_file = sys.argv[1]

    try:
        df = pd.read_csv(csv_file)
        calculate_kpis(df)
    except (OSError, pd.errors.ParserError, ValueError) as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
