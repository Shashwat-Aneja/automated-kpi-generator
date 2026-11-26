import zlib
import gzip
import bz2
import lzma
import io
import argparse
import csv
from numbers import Number
import math
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"date", "amount", "type"}
SUPPORTED_TYPES = {"revenue", "expense"}


def _parse_transaction_dates(values):
    """Parse each date independently so date-only and timestamp strings can coexist."""
    if values.map(lambda value: isinstance(value, Number)).any():
        raise ValueError("Transaction dates must be calendar dates, not numeric epoch offsets.")
    return values.map(lambda value: pd.to_datetime(value, errors="coerce"))


def validate_transactions(df):
    """Return a validated copy with normalized transaction types and numeric amounts."""
    if not isinstance(df, pd.DataFrame) or df.columns.duplicated().any():
        raise ValueError("Transactions require a DataFrame with unique column names.")
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("CSV missing required columns: " + ", ".join(sorted(missing)))
    if df.empty:
        raise ValueError("CSV contains no transaction rows.")

    cleaned = df.copy()
    cleaned["type"] = cleaned["type"].astype("string").str.strip().str.lower()
    if cleaned["amount"].map(lambda value: isinstance(value, (bool, np.bool_))).any():
        raise ValueError("Transaction amounts must be numeric, not booleans.")
    if pd.api.types.is_complex_dtype(cleaned["amount"]):
        raise ValueError("Transaction amounts must be real numbers.")
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    if pd.api.types.is_complex_dtype(cleaned["amount"]):
        raise ValueError("Transaction amounts must be real numbers.")

    parsed_dates = _parse_transaction_dates(cleaned["date"])
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
    parsed_dates = _parse_transaction_dates(cleaned["date"])
    # Compare calendar dates rather than Timestamp objects so mixed timezone
    # offsets do not trigger tz-aware versus tz-naive comparison errors.
    dates = parsed_dates.map(lambda value: value.date())
    try:
        start = pd.Timestamp(start_date).date() if start_date is not None else None
        end = pd.Timestamp(end_date).date() if end_date is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("Date filters must be valid dates in YYYY-MM-DD format.") from exc

    if (start_date is not None and pd.isna(start)) or (end_date is not None and pd.isna(end)):
        raise ValueError("Date filters must be valid dates in YYYY-MM-DD format.")
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


def calculate_kpis(df, print_report=True):
    """Calculate KPIs, print a human-readable report, and return reusable metrics."""
    df = validate_transactions(df)
    revenue_transactions = df.loc[df["type"] == "revenue", "amount"]
    expense_transactions = df.loc[df["type"] == "expense", "amount"]
    # Convert before summing to avoid silent int64 wraparound in pandas sums.
    try:
        revenue = math.fsum(float(value) for value in revenue_transactions)
        expenses = math.fsum(float(value) for value in expense_transactions)
    except OverflowError as exc:
        raise ValueError("KPI totals exceed the supported numeric range.") from exc
    profit = revenue - expenses
    average_revenue_transaction = (
        revenue / len(revenue_transactions) if len(revenue_transactions) else 0
    )
    average_expense_transaction = (
        expenses / len(expense_transactions) if len(expense_transactions) else 0
    )
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0
    if not all(math.isfinite(value) for value in (
        revenue, expenses, profit, profit_margin, expense_ratio,
        average_revenue_transaction, average_expense_transaction,
    )):
        raise ValueError("KPI totals exceed the supported numeric range.")
    transaction_dates = _parse_transaction_dates(df["date"])
    # Mixed UTC offsets cannot be ordered directly; report local calendar dates.
    calendar_dates = transaction_dates.map(lambda timestamp: timestamp.date())

    summary = {
        "total_revenue": float(revenue),
        "total_expenses": float(expenses),
        "profit": float(profit),
        "profit_margin": float(profit_margin),
        "expense_ratio": float(expense_ratio),
        "transaction_count": int(len(df)),
        "revenue_transaction_count": int(len(revenue_transactions)),
        "expense_transaction_count": int(len(expense_transactions)),
        "average_revenue_transaction": float(average_revenue_transaction),
        "average_expense_transaction": float(average_expense_transaction),
        "period_start": calendar_dates.min().isoformat(),
        "period_end": calendar_dates.max().isoformat(),
    }

    if print_report:
        print("\n===== KPI Report =====")
        print(f"Total Revenue      : ₹{revenue}")
        print(f"Total Expenses     : ₹{expenses}")
        print(f"Profit             : ₹{profit}")
        print(f"Profit Margin      : {profit_margin:.2f}%")
        print(f"Expense Ratio      : {expense_ratio:.2f}%")
        print(f"Transactions       : {len(df)}")
        print(f"Average Revenue Tx : ₹{average_revenue_transaction:.2f}")
        print(f"Average Expense Tx : ₹{average_expense_transaction:.2f}")
        print(f"Reporting Period   : {summary['period_start']} to {summary['period_end']}")
        print("Growth Rate        : N/A (single period)")
        print("======================\n")
    return summary


def monthly_kpis(df):
    cleaned = validate_transactions(df)
    months = _parse_transaction_dates(cleaned["date"]).map(lambda value: value.strftime("%Y-%m"))
    return [{"month": month, **calculate_kpis(group, print_report=False)} for month, group in cleaned.groupby(months, sort=True)]


def period_kpis(df, frequency):
    if frequency not in {"month", "quarter", "year"}:
        raise ValueError("Reporting frequency must be month, quarter, or year.")
    cleaned = validate_transactions(df)
    dates = _parse_transaction_dates(cleaned["date"])
    if frequency == "month":
        labels = dates.map(lambda date: date.strftime("%Y-%m"))
    elif frequency == "quarter":
        labels = dates.map(lambda date: f"{date.year:04d}-Q{(date.month - 1) // 3 + 1}")
    else:
        labels = dates.map(lambda date: f"{date.year:04d}")
    return [{"period": label, **calculate_kpis(group, print_report=False)} for label, group in cleaned.groupby(labels, sort=True)]


def export_json(summary, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output_path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(summary, handle, allow_nan=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def compare_periods(current, previous):
    comparison = {}
    for metric in ("total_revenue", "total_expenses", "profit"):
        current_value, previous_value = current[metric], previous[metric]
        delta = current_value - previous_value
        growth = delta / previous_value * 100 if previous_value > 0 else None
        if not math.isfinite(delta) or (growth is not None and not math.isfinite(growth)):
            raise ValueError("Period comparison exceeds the supported numeric range.")
        comparison[metric] = {"change": delta, "growth_percent": growth}
    return comparison


def _reject_duplicate_headers(csv_file, delimiter=","):
    """Inspect original UTF-8 CSV headers without taking ownership of streams."""
    def header_lines(source):
        # csv.reader needs physical lines even for StringIO objects whose default
        # iterator does not recognize CR-only records. Preserve quoted newlines.
        pending = ""
        first = True
        started = False
        while True:
            chars = []
            while True:
                char = pending or source.read(1)
                pending = ""
                if not char:
                    break
                if first:
                    first = False
                    if char == "\ufeff":
                        continue
                chars.append(char)
                if char == "\r":
                    following = source.read(1)
                    if following == "\n":
                        chars.append(following)
                    else:
                        pending = following
                    break
                if char == "\n":
                    break
            if not chars:
                return
            line = "".join(chars)
            if not started and not line.strip():
                continue
            started = True
            yield line

    if isinstance(csv_file, (str, os.PathLike)):
        if not Path(csv_file).is_file():
            return
        opener = {".gz": gzip.open, ".bz2": bz2.open, ".xz": lzma.open}.get(Path(csv_file).suffix, open)
        try:
            with opener(csv_file, mode="rt", encoding="utf-8-sig", newline="") as source:
                headers = next(csv.reader(header_lines(source), delimiter=delimiter), [])
        except (EOFError, lzma.LZMAError, zlib.error, csv.Error) as exc:
            raise ValueError("CSV input is corrupt or incomplete, or its header exceeds parser limits.") from exc
    else:
        if not all(hasattr(csv_file, name) for name in ("read", "seek", "tell")) or (hasattr(csv_file, "seekable") and not csv_file.seekable()):
            raise ValueError("CSV streams must be seekable for header validation.")
        position = csv_file.tell()
        binary = isinstance(csv_file.read(0), bytes)
        source = io.TextIOWrapper(csv_file, encoding="utf-8-sig", newline="") if binary else csv_file
        try:
            headers = next(csv.reader(header_lines(source), delimiter=delimiter), [])
        except (EOFError, lzma.LZMAError, zlib.error, csv.Error) as exc:
            raise ValueError("CSV input is corrupt or incomplete, or its header exceeds parser limits.") from exc
        finally:
            if binary:
                source.detach()
            csv_file.seek(position)
    if len(headers) != len(set(headers)):
        raise ValueError("CSV column names must be unique; duplicate headers are ambiguous.")


def load_transactions(path, delimiter=","):
    if delimiter not in (",", ";", "\t", "|"):
        raise ValueError("Unsupported input delimiter.")
    _reject_duplicate_headers(path, delimiter)
    try:
        return pd.read_csv(path, **({"sep": delimiter} if delimiter != "," else {}))
    except (EOFError, lzma.LZMAError, zlib.error) as exc:
        raise ValueError("CSV input is corrupt or incomplete.") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate KPIs from transaction CSV data.")
    parser.add_argument("csv_file", help="CSV containing date, amount, and type columns")
    parser.add_argument("--start-date", help="Inclusive reporting start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Inclusive reporting end date (YYYY-MM-DD)")
    parser.add_argument("--json-output", help="Atomically save KPI metrics as JSON")
    parser.add_argument("--compare-csv", help="Previous-period CSV for revenue, expense and profit changes")
    parser.add_argument("--json", action="store_true", help="Print only a machine-readable KPI report on success")
    parser.add_argument("--monthly", action="store_true", help="Include calendar-month KPI breakdowns within the selected reporting range")
    parser.add_argument("--delimiter", choices=(",", ";", "tab", "|"), default=",", help="Input CSV delimiter; exports remain comma-separated")
    parser.add_argument("--compare-start-date", help="Inclusive start date within the comparison CSV")
    parser.add_argument("--compare-end-date", help="Inclusive end date within the comparison CSV")
    parser.add_argument("--group-by", choices=("month", "quarter", "year"), help="Include KPI breakdowns by calendar reporting period")
    args = parser.parse_args(argv)
    if args.monthly and args.group_by:
        parser.error("Use --monthly or --group-by, not both")
    if (args.compare_start_date is not None or args.compare_end_date is not None) and not args.compare_csv:
        parser.error("Comparison date filters require --compare-csv")
    delimiter = "\t" if args.delimiter == "tab" else args.delimiter

    try:
        df = load_transactions(args.csv_file, **({"delimiter": delimiter} if delimiter != "," else {}))
        if args.start_date is not None or args.end_date is not None:
            df = filter_transactions_by_period(
                df, start_date=args.start_date, end_date=args.end_date
            )
        summary = calculate_kpis(df, print_report=not args.json)
        if args.monthly:
            summary["monthly"] = monthly_kpis(df)
            if not args.json:
                print("Monthly KPIs:", json.dumps(summary["monthly"], allow_nan=False))
        if args.group_by:
            summary["period_breakdown"] = {"frequency": args.group_by, "periods": period_kpis(df, args.group_by)}
            if not args.json:
                print("Period KPIs:", json.dumps(summary["period_breakdown"], allow_nan=False))
        if args.compare_csv:
            previous_frame = load_transactions(args.compare_csv, **({"delimiter": delimiter} if delimiter != "," else {}))
            if args.compare_start_date is not None or args.compare_end_date is not None:
                previous_frame = filter_transactions_by_period(previous_frame, args.compare_start_date, args.compare_end_date)
            previous = calculate_kpis(previous_frame, print_report=not args.json)
            summary["comparison"] = compare_periods(summary, previous)
            summary["comparison_period"] = {"period_start": previous["period_start"], "period_end": previous["period_end"], "overlaps_current": summary["period_start"] <= previous["period_end"] and previous["period_start"] <= summary["period_end"]}
            if not args.json:
                print("Period comparison:", json.dumps(summary["comparison"], allow_nan=False))
                if summary["comparison_period"]["overlaps_current"]:
                    print("Comparison period overlaps the current reporting period.")
        if args.json_output:
            source = Path(args.csv_file).resolve()
            output = Path(args.json_output).expanduser().resolve()
            protected = [source]
            if args.compare_csv:
                protected.append(Path(args.compare_csv).resolve())
            if any(output == path or (output.exists() and output.samefile(path)) for path in protected):
                raise ValueError("JSON output must differ from the input CSV.")
            export_json(summary, output)
        if args.json:
            print(json.dumps(summary, allow_nan=False))
        return 0
    except (OSError, pd.errors.ParserError, ValueError) as exc:
        print(f"❌ Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

