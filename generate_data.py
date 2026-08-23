"""
STEP 1: Generate fake (synthetic) data.
This pretends to be a batch of failed payments and abandoned checkouts,
like what a real merchant on Razorpay would have.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # keeps results the same every time you run it

FAILURE_REASONS = [
    "insufficient_funds",
    "bank_timeout",
    "card_expired",
    "issuer_declined",
    "network_error",
]

PAYMENT_METHODS = ["UPI", "credit_card", "debit_card", "netbanking"]

EVENT_TYPES = ["failed_payment", "checkout_abandoned", "subscription_failed"]


def random_timestamp():
    days_ago = random.randint(0, 30)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")


def generate_records(n=120):
    records = []
    for i in range(1, n + 1):
        event_type = random.choices(
            EVENT_TYPES, weights=[0.55, 0.30, 0.15]
        )[0]

        record = {
            "transaction_id": f"TXN{1000 + i}",
            "customer_id": f"CUST{random.randint(100, 250)}",
            "amount": round(random.uniform(150, 15000), 2),
            "payment_method": random.choice(PAYMENT_METHODS),
            "event_type": event_type,
            "timestamp": random_timestamp(),
            "retry_count": random.choice([0, 0, 0, 1, 1, 2]),  # mostly 0
        }

        # only failed/subscription events have a failure_reason
        if event_type in ("failed_payment", "subscription_failed"):
            record["failure_reason"] = random.choice(FAILURE_REASONS)
        else:
            record["failure_reason"] = "abandoned"  # no reason given, just left

        # a few deliberately messy records (real data is never perfectly clean)
        if random.random() < 0.05:
            record["failure_reason"] = ""  # missing/unknown reason

        records.append(record)
    return records


def save_to_csv(records, filename="data.csv"):
    fieldnames = [
        "transaction_id", "customer_id", "amount", "payment_method",
        "event_type", "timestamp", "retry_count", "failure_reason",
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Created {filename} with {len(records)} records.")


if __name__ == "__main__":
    records = generate_records(120)
    save_to_csv(records)
