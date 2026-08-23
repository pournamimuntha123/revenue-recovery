"""
STEP 7: AI-powered classification for AMBIGUOUS cases only.

Why only ambiguous cases? Because using AI everywhere is wasteful and
slower. The "right tool in the right place" means: simple, clear cases
(card expired, network error) use fast rule-based logic. Only genuinely
unclear cases (blank/unknown failure reason) get a real AI judgment call.

If no API key is available, this safely falls back to the same
conservative rule-based guess as before -- so the project still runs
for anyone without a key.
"""

import os
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def classify_with_ai(record):
    """
    Uses Claude to make a careful judgment call on an ambiguous case.
    Returns (reason, confidence) just like the rule-based classifier.
    Falls back safely if no API key or library is available.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not ANTHROPIC_AVAILABLE or not api_key:
        # Safe fallback: same conservative behavior as before
        return "issuer_declined", "low"

    try:
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""A payment failed with these details, but the failure
reason is missing or unclear:

Amount: {record.get('amount')}
Payment method: {record.get('payment_method')}
Event type: {record.get('event_type')}
Retry count so far: {record.get('retry_count')}

Based on this, what is the MOST LIKELY failure reason? Choose exactly
one from this list: insufficient_funds, bank_timeout, card_expired,
issuer_declined, network_error.

Respond with ONLY valid JSON, nothing else, in this exact format:
{{"reason": "one_of_the_options_above", "confidence": "low_or_medium"}}
"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)

        reason = result.get("reason", "issuer_declined")
        confidence = result.get("confidence", "low")
        return reason, confidence

    except Exception as e:
        # If the AI call fails for any reason, fall back safely
        # rather than crashing the whole pipeline.
        print(f"  [AI classification failed, using safe fallback: {e}]")
        return "issuer_declined", "low"
