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
