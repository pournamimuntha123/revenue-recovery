"""
STEP 4: Main script. Run this one file to run the whole project.

    python3 main.py

It will:
  1. Load the data (data.csv)
  2. Classify + decide an action for every transaction
  3. Simulate whether the action recovered the money
  4. Print a results summary
  5. Save a full audit log to audit_log.csv
"""

import csv
from recovery_engine import process_record
from simulate_outcomes import simulate_outcome, compute_metrics


def load_data(filename="data.csv"):
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_audit_log(audit_entries, filename="audit_log.csv"):
    fieldnames = [
        "transaction_id", "amount", "event_type", "classified_reason",
        "confidence", "action_taken", "explanation", "recovered", "amount_recovered",
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_entries)
    print(f"\nFull audit trail saved to {filename}")


def print_report(metrics):
    print("\n" + "=" * 50)
    print("REVENUE RECOVERY REPORT")
    print("=" * 50)
    print(f"Total transactions processed : {metrics['total_transactions']}")
    print(f"Total amount at risk         : Rs {metrics['total_amount_at_risk']:,}")
    print(f"Total amount recovered       : Rs {metrics['total_amount_recovered']:,}")
    print(f"Recovery rate                : {metrics['recovery_rate_pct']}%")
    print(f"Transactions recovered       : {metrics['transactions_recovered']}")
    print(f"Escalated to human           : {metrics['escalation_rate_pct']}%")
    print("\nBreakdown by action taken:")
    for action, stats in metrics["breakdown_by_action"].items():
        print(f"  - {action:30s} count={stats['count']:3d}  "
              f"recovered={stats['recovered']:3d}  "
              f"amount_recovered=Rs {round(stats['amount_recovered'], 2):,}")
    print("=" * 50)


def main():
    print("Loading data...")
    records = load_data()
    print(f"Loaded {len(records)} records.")

    print("Classifying and deciding actions...")
    audit_entries = [process_record(r) for r in records]

    print("Simulating recovery outcomes...")
    audit_entries = [simulate_outcome(e) for e in audit_entries]

    metrics = compute_metrics(audit_entries)
    print_report(metrics)
    save_audit_log(audit_entries)


if __name__ == "__main__":
    main()
