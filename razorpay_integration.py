"""
STEP 8: Real Razorpay test-mode API integration.

This is NOT simulated -- it actually calls Razorpay's live test-mode API
using the official razorpay Python SDK.

WHY PAYMENT LINKS: Razorpay does not let you "force retry" a customer's
card directly via API (that requires the customer's card details, which
merchants never store). The real, supported way to recover a failed
payment is to generate a fresh Payment Link and send it to the customer --
this is exactly what "retry" and "nudge" actions map onto in production.

HOW TO USE:
1. Sign up at razorpay.com, switch dashboard to TEST MODE (toggle top-left)
2. Go to Settings -> API Keys -> Generate Test Key
3. In Command Prompt, before running main.py, set:
     set RAZORPAY_KEY_ID=your_test_key_id
     set RAZORPAY_KEY_SECRET=your_test_key_secret
4. pip install razorpay

If no keys are set, this safely skips real API calls and returns a
clearly-labeled placeholder instead -- so the rest of the project still
runs fine without a Razorpay account.
"""

import os

try:
    import razorpay
    RAZORPAY_SDK_AVAILABLE = True
except ImportError:
    RAZORPAY_SDK_AVAILABLE = False


def get_client():
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")

    if not RAZORPAY_SDK_AVAILABLE or not key_id or not key_secret:
        return None

    return razorpay.Client(auth=(key_id, key_secret))


def create_recovery_payment_link(record, action):
    """
    Actually calls Razorpay's TEST MODE API to create a real payment link
    for this transaction, so the customer can complete payment again.

    Returns a dict with the real link details, or a clearly-labeled
    placeholder if no API keys are configured.
    """
    client = get_client()

    if client is None:
        return {
            "status": "skipped_no_api_key",
            "note": "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to make real API calls",
            "payment_link_url": None,
        }

    # Only create real links for actions that actually involve asking the
    # customer to pay again -- not for pure escalate_to_human cases.
    actionable = {"retry_in_48h", "retry_immediately", "notify_customer_update_card", "send_checkout_reminder"}
    if action not in actionable:
        return {"status": "not_applicable", "payment_link_url": None}

    amount_paise = int(float(record["amount"]) * 100)  # Razorpay uses paise, not rupees

    description_map = {
        "retry_in_48h": "Retry payment - funds likely available now",
        "retry_immediately": "Retry payment - previous attempt had a technical issue",
        "notify_customer_update_card": "Update your card to complete this payment",
        "send_checkout_reminder": "Complete your checkout - items still reserved",
    }

    try:
        link = client.payment_link.create({
            "amount": amount_paise,
            "currency": "INR",
            "description": description_map.get(action, "Complete your payment"),
            "reference_id": record["transaction_id"],
            "notify": {"sms": False, "email": False},  # test mode: don't actually send
            "notes": {
                "original_transaction_id": record["transaction_id"],
                "recovery_action": action,
            },
        })
        return {
            "status": "created",
            "payment_link_url": link.get("short_url"),
            "razorpay_link_id": link.get("id"),
        }
    except Exception as e:
        return {
            "status": "api_error",
            "error": str(e),
            "payment_link_url": None,
        }


def check_api_connection():
    """
    Simple check: can we actually reach Razorpay's test API with these keys?
    Useful to run once before processing a whole batch.
    """
    client = get_client()
    if client is None:
        print("Razorpay API: not configured (no keys set). Running in simulation-only mode.")
        return False

    try:
        # fetching payment methods is a lightweight way to confirm auth works
        client.payment_link.all({"count": 1})
        print("Razorpay API: connected successfully in TEST MODE.")
        return True
    except Exception as e:
        print(f"Razorpay API: connection failed - {e}")
        return False
