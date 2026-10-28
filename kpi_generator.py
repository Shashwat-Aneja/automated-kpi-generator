import argparse
import math

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


def filter_transactions_by_period(df, start_date=None, end_date=None):
    """Filter validated transactions by inclusive calendar dates."""
    cleaned = validate_transactions(df)
    dates = pd.to_datetime(cleaned["date"]).dt.normalize()
    try:
        start = pd.Timestamp(start_date).normalize() if start_date is not None else None
        end = pd.Timestamp(end_date).normalize() if end_date is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("Date filters must be valid dates in YYYY-MM-DD format.") from exc

    if start is not None and end is not None and start > end:
        raise ValueError("Start date must be on or before end date.")

    mask = pd.Series(True, index=cleaned.index)
    if start is not None:
        mask &= dates >= start
    if end is not None:
        mask &= dates <= end
    filtered = cleaned.loc[mask].copy()
    if filtered.empty:
        raise ValueError("No transactions found within the selected date range.")
    return filtered


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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate KPIs from transaction CSV data.")
    parser.add_argument("csv_file", help="CSV containing date, amount, and type columns")
    parser.add_argument("--start-date", help="Inclusive reporting start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Inclusive reporting end date (YYYY-MM-DD)")
    args = parser.parse_args(argv)

    try:
        df = pd.read_csv(args.csv_file)
        if args.start_date is not None or args.end_date is not None:
            df = filter_transactions_by_period(
                df, start_date=args.start_date, end_date=args.end_date
            )
        calculate_kpis(df)
        return 0
    except (OSError, pd.errors.ParserError, ValueError) as exc:
        print(f"❌ Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
