"""
STEP 3: Simulate whether each recovery action succeeded.
In real life this would come from actually retrying the payment via
Razorpay's API. Here we simulate it with realistic success rates,
since we're working with test/synthetic data.

IMPORTANT: Be honest about this in your video/README -- these success
rates are simulated assumptions, not measured real-world outcomes.
"""

import random

random.seed(7)

# realistic-ish success rates per action (this is an assumption, state it clearly)
SUCCESS_RATES = {
    "retry_in_48h": 0.42,
    "retry_immediately": 0.55,
    "notify_customer_update_card": 0.28,
    "send_checkout_reminder": 0.22,
    "escalate_to_human": 0.15,  # humans still recover some, just slower
}


def simulate_outcome(audit_entry):
    action = audit_entry["action_taken"]
    success_rate = SUCCESS_RATES.get(action, 0.1)
    recovered = random.random() < success_rate
    audit_entry["recovered"] = recovered
    audit_entry["amount_recovered"] = audit_entry["amount"] if recovered else 0.0
    return audit_entry


def compute_metrics(audit_entries):
    total_amount = sum(e["amount"] for e in audit_entries)
    total_recovered = sum(e["amount_recovered"] for e in audit_entries)
    total_count = len(audit_entries)
    recovered_count = sum(1 for e in audit_entries if e["recovered"])

    escalated = [e for e in audit_entries if e["action_taken"] == "escalate_to_human"]
    escalation_rate = len(escalated) / total_count if total_count else 0

    # breakdown by action taken
    by_action = {}
    for e in audit_entries:
        action = e["action_taken"]
        by_action.setdefault(action, {"count": 0, "recovered": 0, "amount_recovered": 0.0})
        by_action[action]["count"] += 1
        if e["recovered"]:
            by_action[action]["recovered"] += 1
        by_action[action]["amount_recovered"] += e["amount_recovered"]

    return {
        "total_transactions": total_count,
        "total_amount_at_risk": round(total_amount, 2),
        "total_amount_recovered": round(total_recovered, 2),
        "recovery_rate_pct": round((total_recovered / total_amount) * 100, 2) if total_amount else 0,
        "transactions_recovered": recovered_count,
        "escalation_rate_pct": round(escalation_rate * 100, 2),
        "breakdown_by_action": by_action,
    }
