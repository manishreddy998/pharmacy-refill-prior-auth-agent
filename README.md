# Pharmacy workflow agent with guardrails and escalation

**Problem.** Refills and prior authorizations eat pharmacy staff time. An agent can do the routine cases, but it must never auto approve something a pharmacist has to see, such as a controlled substance, an allergy flag or an unverified identity.

**Architecture.** `rxagent/tools.py` has a fake pharmacy back end with 7 drugs and payer prior authorization rules. Its ground truth policy is written separately from the agent. `rxagent/agent.py` runs a tool loop. A planner picks the next tool. That planner can be an LLM, and here it is a deterministic stub. Hard guardrails run first. Every tool has preconditions, unknown tools escalate, there is a step budget, and every step goes into a trace for audit. `rxagent/evaluate.py` scores 300 seeded cases. It also runs a planner that makes a random wrong choice 20% of the time, to show what happens when the model misbehaves.

**Results** (`python -m rxagent.evaluate`, results.json)

| planner | accuracy | unsafe auto actions | escalated | avg tool calls |
|---|---|---|---|---|
| deterministic stub | 1.000 (300/300) | 0 | 79 | 1.58 |
| 20% bad tool choices | 0.903 (271/300) | 0 | 108 | 1.73 |

**What the eval caught.** The first noisy planner run crashed. A tool could run before the drug lookup, and a refill check could run on a prior authorization case. Adding tool preconditions fixed both. Now bad model choices only turn into extra escalations, never into unsafe approvals.

**Limits.** All data is synthetic and seeded, so every run gives the same cases. The policy is simplified. No real payer API or LLM is called.

Tests: `pytest -q` (4 tests).

## Data

All patients, prescriptions and payer rules are synthetic and generated from a fixed seed. No real patient data is used.

## Author

Manish Reddy, [LinkedIn](https://linkedin.com/in/manish-re-50c02a719k)
