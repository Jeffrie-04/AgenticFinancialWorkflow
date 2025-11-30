import json
from collections import defaultdict

# Load the categorized.json file
with open("outputs/categorized.json", "r") as f:
    data = json.load(f)

transactions = data["categorized"]

total_spend = 0.0
total_income = 0.0
expense_list = []

# Track spend by merchant
merchant_spend = defaultdict(float)

for t in transactions:
    amount = float(t["amount"])
    merchant = t["merchant"]

    if amount < 0:
        # Negative = income
        total_income += abs(amount)
    else:
        # Positive = expense
        total_spend += amount
        expense_list.append(amount)
        merchant_spend[merchant] += amount

# --- DERIVED METRICS (UNROUNDED) ---

# Average expense from dataset
average_expense_raw = (
    sum(expense_list) / len(expense_list) if expense_list else 0.0
)

# Top 3 merchants by total spend amount (unrounded)
sorted_merchants = sorted(
    merchant_spend.items(), key=lambda x: x[1], reverse=True
)
top_merchants = [m for m, _ in sorted_merchants[:3]]

# --- VALIDATION SECTION ---

# 1) Total spend > 0
if total_spend <= 0:
    raise ValueError(f"Validation failed: total_spend <= 0 (got {total_spend})")

# 2) Total income aligns with known Paycheck/Deposit (Income category) rows
income_from_category = sum(
    -t["amount"] for t in transactions if t.get("category") == "Income"
)

if abs(total_income - income_from_category) > 1e-6:
    raise ValueError(
        f"Validation failed: total_income ({total_income}) "
        f"!= sum(Income category) ({income_from_category})"
    )

# 3) Top merchants list is accurate (matches recomputed ranking)
recomputed_top3 = [m for m, _ in sorted_merchants[:3]]
if top_merchants != recomputed_top3:
    raise ValueError(
        "Validation failed: top_merchants list does not match computed top 3 "
        f"(got {top_merchants}, expected {recomputed_top3})"
    )

# 4) Average expense matches dataset
recomputed_avg = sum(expense_list) / len(expense_list) if expense_list else 0.0
if abs(average_expense_raw - recomputed_avg) > 1e-6:
    raise ValueError(
        "Validation failed: average_expense does not match dataset "
        f"(got {average_expense_raw}, expected {recomputed_avg})"
    )

print("All validations passed successfully.")

# --- ROUNDING FOR OUTPUT ---

result = {
    "kpis": {
        "total_spend": round(total_spend, 2),
        "total_income": round(total_income, 2),
        "top_merchants": top_merchants,
        "average_expense": round(average_expense_raw, 2),
    }
}

# Write to JSON file only AFTER validations succeed
with open("outputs/kpis.json", "w") as f:
    json.dump(result, f, indent=2)

print("KPIs saved to kpis.json")