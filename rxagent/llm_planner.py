"""Real LLM planner: local Qwen2.5 3B (Ollama) picks the next tool name. It sees the case and
the state so far, never the guardrail result, and it can only return a tool name. Replays from
data/llm_cache.json; set LLM=ollama to run live."""
import json
from .llm import get_backend

SYS = ("You are a pharmacy workflow planner. Pick the next tool. Tools: lookup_drug (always first), "
       "check_refills (refill cases, after lookup_drug), check_formulary (prior_auth cases, after lookup_drug), "
       "check_chart (prior_auth cases, after check_formulary says PA is required). Reply JSON {\"tool\": \"name\"}.")


def make_llm_planner():
    be = get_backend()
    def plan(c, state):
        p = f"Case: {c['kind']} for {c['drug']}, payer {c['payer']}.\nState so far: {json.dumps(state)}\nNext tool?"
        try:
            return str(be.complete_json(SYS, p, 24).get("tool", "none"))
        except KeyError:
            raise
        except Exception:
            return "invalid_output"
    return plan
