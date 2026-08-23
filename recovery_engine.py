"""
STEP 2: The decision engine.
For every failed payment or abandoned checkout, this decides:
  1. Why did it fail? (classify)
  2. What should we do about it? (route to an action)
  3. Are we allowed to act, or must we stop? (stopping rules)

Every decision is written down (audited), so nothing happens silently.
"""

MAX_RETRIES = 3


def classify(record):
    """
    STEP 2a: Work out the failure reason.
    Most records already have a clear reason from the data.
    If it's missing, we make a careful guess instead of blindly retrying.
    """
    reason = record.get("failure_reason", "").strip()

    if reason:
        return reason, "high"  # confidence: high, because reason is known

    # missing reason -> fall back to a safe guess based on amount + method
    if record["event_type"] == "checkout_abandoned":
        return "abandoned", "high"

    # unknown failure reason: guess "issuer_declined" (safest, most conservative)
    return "issuer_declined", "low"


def decide_action(record, reason, confidence):
    """
    STEP 2b: Decide the recovery action, and enforce stopping rules
    so nothing retries forever or annoys the customer.
    """
    retry_count = int(record["retry_count"])

    # STOPPING RULE 1: too many retries already -> stop, hand to a human
    if retry_count >= MAX_RETRIES:
        return "escalate_to_human", "Max retries already reached; stopping automatic attempts."

    # STOPPING RULE 2: low-confidence classification -> don't act blindly
    if confidence == "low":
        return "escalate_to_human", "Failure reason unclear; routed to human review instead of guessing."

    # Now route based on the reason
    if reason == "insufficient_funds":
        return "retry_in_48h", "Funds often replenish within 1-2 days (e.g. salary credit); scheduled a delayed retry."

    if reason in ("bank_timeout", "network_error"):
        return "retry_immediately", "Transient technical failure; safe to retry right away."

    if reason == "card_expired":
        return "notify_customer_update_card", "Card is expired; retrying won't help, so we ask the customer to update it."

    if reason == "issuer_declined":
        return "escalate_to_human", "Bank declined the payment; automatic retries risk more declines, so a human should review."

    if reason == "abandoned":
        return "send_checkout_reminder", "Customer left without paying; a gentle reminder often recovers the sale."

    # fallback safety net: never leave a case unhandled
    return "escalate_to_human", "Unrecognized case; defaulting to safe human review."


def process_record(record):
    """
    STEP 2c: Run one record through classify -> decide -> log.
    Returns a full audit entry.
    """
    reason, confidence = classify(record)
    action, explanation = decide_action(record, reason, confidence)

    audit_entry = {
        "transaction_id": record["transaction_id"],
        "amount": float(record["amount"]),  # CSV gives text; convert to a real number
        "event_type": record["event_type"],
        "classified_reason": reason,
        "confidence": confidence,
        "action_taken": action,
        "explanation": explanation,
    }
    return audit_entry
