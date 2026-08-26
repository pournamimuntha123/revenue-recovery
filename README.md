# Revenue Recovery Agent

Recovers money from failed payments and abandoned checkouts by figuring out
*why* each one happened and choosing the right, bounded next action — instead
of blindly retrying everything.

## Problem

Failed payments and abandoned checkouts are one of the largest silent revenue
leaks for merchants. Most of these are recoverable if you retry at the right
time, or nudge the customer the right way — but doing this by hand doesn't
scale, and doing it carelessly (retrying forever, spamming customers) causes
its own problems.

## How it works

```
failed payment / abandoned checkout
        |
        v
   CLASSIFY  --> why did this happen? (known reason, or careful guess)
        |
        v
   DECIDE ACTION --> retry now / retry later / ask customer / escalate to human
        |
        v
   STOPPING RULES --> max retries, low-confidence cases go to a human, never spam
        |
        v
   AUDIT LOG --> every decision is recorded with its reason
```

## Run it

```bash
pip install -r requirements.txt   # (no external dependencies needed, standard library only)
python3 generate\\\_data.py          # creates data.csv (120 synthetic transactions)
python3 main.py                   # runs the full pipeline and prints the report
```

Output:

* Console report with headline numbers
* `audit\\\_log.csv` — full decision trail for every transaction

## Results (on this synthetic batch)

|Metric|Value|
|-|-|
|Total transactions|120|
|Total amount at risk|Rs 891,229|
|Total amount recovered|Rs 261,495|
|Recovery rate|29.34%|
|Escalated to human|19.17%|

*(Recovery outcomes are simulated with assumed success rates per action, since
this uses synthetic data rather than live Razorpay transactions. See
`simulate\\\_outcomes.py` for the assumed rates.)*

## Stopping rules (the "bounded" part)

* Max 3 retries per transaction, then automatic escalation to a human
* Low-confidence classifications never trigger an automatic retry — they go
straight to human review instead of guessing
* Every action is logged with a plain-English reason, so nothing happens silently

## What broke, and how it was fixed

The pipeline initially crashed while computing total recovered amount. Data
loaded from CSV comes in as text, and the amount field wasn't converted to a
number before being summed, causing a `TypeError`. Fixed by explicitly
converting `record\\\["amount"]` to `float()` when building each audit entry.
This is a good example of why every stage should validate its inputs instead
of assuming the previous stage's output is the right type.



&#x20;  ## AI usage



&#x20;  Most cases use fast rule-based classification, since the failure reason is

&#x20;  already known. Only genuinely ambiguous cases (missing/unclear failure

&#x20;  reason) are sent to an AI model (Claude) for a careful judgment call. This

&#x20;  keeps the system fast and cheap for clear cases, and uses AI only where it

&#x20;  adds real value — not everywhere.



\## Real API integration (designed, not fully activated)



The system is designed to integrate with Razorpay's Payment Links API via

`razorpay\_integration.py`, generating real recovery payment links for

customers. Full activation requires Razorpay test-mode API keys, which

require account KYC including bank verification — this repo demonstrates

the integration code path with simulated outcomes, and switches to real

API calls automatically once keys are configured.



\## Dashboard



Run `streamlit run dashboard.py` for an interactive view of results,

including metric cards, charts by action type and failure reason, and a

filterable transaction-level table.





## Known limitations

* Recovery outcomes are simulated, not real — a production version would call
Razorpay's actual retry/notification APIs and measure real outcomes
* Classification is rule-based for known failure reasons; an LLM-based
classifier could handle messier, unstructured failure messages better
* Compliance rules (e.g. DND preferences, opt-outs) are simplified here and
would need real regulatory input for production use

## Files

* `generate\\\_data.py` — creates synthetic transaction data
* `recovery\\\_engine.py` — classification + decision + stopping rules
* `simulate\\\_outcomes.py` — simulates outcomes and computes metrics
* `main.py` — runs everything end-to-end
* `data.csv` — generated input data
* `audit\\\_log.csv` — generated output (full decision trail)

