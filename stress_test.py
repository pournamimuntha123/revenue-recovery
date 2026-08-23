"""
STEP 5: Stress test.
Creates a small batch of deliberately tricky records and checks that our
stopping rules handle them safely. This is proof (not just a claim) that
the system is "bounded and gated" as required.

Run with:  py stress_test.py
"""

from recovery_engine import process_record

# Deliberately tricky / edge-case records
edge_cases = [
    {
        "transaction_id": "EDGE001",
        "amount": "5000",
        "event_type": "failed_payment",
        "failure_reason": "insufficient_funds",
        "retry_count": "5",  # already retried way too many times
    },
    {
        "transaction_id": "EDGE002",
        "amount": "12000",
        "event_type": "failed_payment",
        "failure_reason": "",  # missing/unknown reason
        "retry_count": "0",
    },
    {
        "transaction_id": "EDGE003",
        "amount": "800",
        "event_type": "failed_payment",
        "failure_reason": "issuer_declined",
        "retry_count": "3",  # exactly at the max retry limit
    },
    {
        "transaction_id": "EDGE004",
        "amount": "3000",
        "event_type": "checkout_abandoned",
        "failure_reason": "abandoned",
        "retry_count": "0",
    },
    {
        "transaction_id": "EDGE005",
        "amount": "999999",  # unusually large amount
        "event_type": "failed_payment",
        "failure_reason": "network_error",
        "retry_count": "0",
    },
]

expectations = {
    "EDGE001": "escalate_to_human",   # too many retries -> must stop, not retry again
    "EDGE002": "escalate_to_human",   # unknown reason -> must not guess and act
    "EDGE003": "escalate_to_human",   # at max retries -> must stop
    "EDGE004": "send_checkout_reminder",
    "EDGE005": "retry_immediately",   # large amount, transient error -> still safe to retry
}


def run_stress_test():
    print("Running stress test on edge cases...\n")
    all_passed = True

    for record in edge_cases:
        result = process_record(record)
        txn_id = result["transaction_id"]
        expected = expectations[txn_id]
        actual = result["action_taken"]
        passed = actual == expected

        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"[{status}] {txn_id}: expected='{expected}' got='{actual}'")
        print(f"        reason: {result['explanation']}\n")

    print("=" * 50)
    if all_passed:
        print("ALL STOPPING RULES PASSED. System is behaving safely on edge cases.")
    else:
        print("SOME CHECKS FAILED. Review the rules in recovery_engine.py.")
    print("=" * 50)


if __name__ == "__main__":
    run_stress_test()
