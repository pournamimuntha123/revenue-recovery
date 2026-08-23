"""
STEP 6: Make a chart from the results.
This creates a picture (recovery_chart.png) you can show on screen during
your pitch video -- much clearer than reading numbers off a table.

Run with:  py make_chart.py
(Run this AFTER main.py, since it reads audit_log.csv)
"""

import csv
import matplotlib.pyplot as plt

def load_audit_log(filename="audit_log.csv"):
    with open(filename, "r") as f:
        return list(csv.DictReader(f))

def make_chart():
    rows = load_audit_log()

    # group amount_recovered by action_taken
    totals = {}
    for row in rows:
        action = row["action_taken"]
        amount = float(row["amount_recovered"])
        totals[action] = totals.get(action, 0) + amount

    actions = list(totals.keys())
    amounts = [totals[a] for a in actions]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(actions, amounts, color="#4C72B0")
    plt.title("Amount Recovered by Action Type", fontsize=14, fontweight="bold")
    plt.ylabel("Amount Recovered (Rs)")
    plt.xticks(rotation=20, ha="right")

    # label each bar with its value
    for bar, amount in zip(bars, amounts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                  f"Rs {amount:,.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig("recovery_chart.png", dpi=150)
    print("Saved chart to recovery_chart.png")

if __name__ == "__main__":
    make_chart()
