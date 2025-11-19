import pandas as pd
import sys

def calculate_kpis(df):
    revenue = df[df["type"] == "revenue"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    profit = revenue - expenses
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0

    print("\n===== KPI Report =====")
    print(f"Total Revenue      : ₹{revenue}")
    print(f"Total Expenses     : ₹{expenses}")
    print(f"Profit             : ₹{profit}")
    print(f"Profit Margin      : {profit_margin:.2f}%")
    print(f"Expense Ratio      : {expense_ratio:.2f}%")
    print(f"Growth Rate        : N/A (single period)")  # Future enhancement
    print("======================\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python kpi_generator.py <csv_file>")
        return

    csv_file = sys.argv[1]

    try:
        df = pd.read_csv(csv_file)
        if not {"date", "amount", "type"}.issubset(df.columns):
            print("❌ CSV missing required columns: date, amount, type")
            return

        calculate_kpis(df)

    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    main()
