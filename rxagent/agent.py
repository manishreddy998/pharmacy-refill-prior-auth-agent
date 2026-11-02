"""Tool calling style agent loop. Each step picks a tool from observed state; a planner
(LLM or the deterministic stub here) can only choose among allowed tools, and hard
guardrails run before any action leaves the system."""
from .tools import DRUGS
class Trace(list):
    def log(self,step,**kw): self.append(dict(step=step,**kw))
def guardrails(c,tr):
    if c["dob"] is None: tr.log("guard",why="identity not verified"); return "escalate_pharmacist"
    if c["allergy_flag"]: tr.log("guard",why="allergy flag"); return "escalate_pharmacist"
    if DRUGS[c["drug"]]["controlled"]: tr.log("guard",why="controlled substance"); return "escalate_pharmacist"
def planner_stub(c,state):
    if "drug_info" not in state: return "lookup_drug"
    if c["kind"]=="refill": return "check_refills"
    if "pa_rule" not in state: return "check_formulary"
    return "check_chart"
def run_case(c,planner=planner_stub,max_steps=6):
    tr=Trace(); g=guardrails(c,tr)
    if g: return g,tr
    state={}
    for _ in range(max_steps):
        tool=planner(c,state); tr.log("tool",name=tool)
        pre={"check_refills":c["kind"]=="refill" and "drug_info" in state,"check_formulary":c["kind"]=="prior_auth" and "drug_info" in state,"check_chart":state.get("pa_rule") is True}
        if tool in pre and not pre[tool]: tr.log("reject",name=tool,why="precondition not met"); continue
        if tool=="lookup_drug": state["drug_info"]=DRUGS.get(c["drug"])
        elif tool=="check_refills": return ("approve_refill" if c["refills_left"]>0 else "request_prescriber"),tr
        elif tool=="check_formulary":
            state["pa_rule"]=state["drug_info"]["pa"]
            if not state["pa_rule"]: return "no_pa_needed",tr
        elif tool=="check_chart": return ("submit_pa" if c["has_diagnosis"] else "request_prescriber"),tr
        else: tr.log("guard",why=f"unknown tool {tool}"); return "escalate_pharmacist",tr
    tr.log("guard",why="step budget"); return "escalate_pharmacist",tr
