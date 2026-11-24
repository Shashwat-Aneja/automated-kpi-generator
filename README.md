# Automated KPI Generator

A Python-based tool that reads business transaction data (CSV) and automatically calculates key performance indicators (KPIs). Useful for financial automation, decision-making, and business analytics.

---

## 📊 Supported KPIs

| KPI | Description |
|-----|-------------|
| Total Revenue | Sum of income transactions |
| Total Expenses | Sum of expense transactions |
| Profit | Revenue – Expenses |
| Profit Margin | (Profit / Revenue) × 100 |
| Expense Ratio | (Expenses / Revenue) × 100 |
| Growth Rate | Based on previous period (if data available) |

---

## 🧪 Example CSV Format

```
date,amount,type
2025-01-01,5000,revenue
2025-01-02,1200,expense
2025-01-03,3000,revenue
2025-01-04,800,expense
```

---

## 🚀 Usage

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Shashwat-Aneja/automated-kpi-generator
cd automated-kpi-generator
```

### 2️⃣ Install dependencies
```bash
pip install pandas
```

### 3️⃣ Run the script
```bash
python kpi_generator.py data.csv
```

---

## 🔎 Example Output

```
===== KPI Report =====
Total Revenue      : ₹8000
Total Expenses     : ₹2000
Profit             : ₹6000
Profit Margin      : 75.00%
Expense Ratio      : 25.00%
Growth Rate        : N/A (single period)
======================
```

---

## 📁 Project Structure

```
automated-kpi-generator/
│
├── kpi_generator.py
└── README.md
```

---

## 🚀 Future Enhancements
- Add monthly comparison
- Visual charts using matplotlib
- Export KPI report to PDF or CSV
- Integrate with FastAPI (XYLO-compatible)

---

Developed by **Shashwat Aneja**

Use `--json-output metrics.json` to atomically export the returned KPI metrics for automation. The input CSV is protected from overwrite.

`--compare-csv previous.csv` adds changes in revenue, expenses and profit to the report and JSON output. Percentage growth is undefined (`null`) for zero or negative previous values. Date filters apply to the current CSV; the comparison file defines its own prior period.


`--json` prints only the KPI object on success, including optional period comparisons, for scripts and pipelines. Validation failures retain nonzero exit status.

`--monthly` adds sorted calendar-month KPI objects using only rows in the chosen date range. Month assignment follows each transaction’s local calendar date, consistent with the main report.

`--delimiter ";"`, `--delimiter tab` and `--delimiter "|"` support alternate input CSV separators, including quoted fields. Duplicate-header validation uses the selected separator. The default input and all CSV exports remain comma-separated.

Seekable caller-owned text and UTF-8 binary CSV streams now receive the same duplicate-header checks as file paths, before pandas can rename ambiguous columns. Validation restores the starting position and leaves caller streams open; nonseekable stream objects are rejected explicitly.

Comparison reports disclose the prior file’s actual date range and whether it overlaps the current reporting range. Overlap is informational and does not block comparison; JSON output retains the same growth calculations with this additional context.

CSV paths ending in `.gz`, `.bz2`, or `.xz` are supported without unpacking a separate file. Header validation reads the same compression format as pandas and still rejects duplicate columns, including BOM-prefixed quoted headers and alternate delimiters. Archive containers such as ZIP/TAR are outside this feature.
