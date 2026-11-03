"""Pharmacy back end. Drug facts are REAL: controlled status and DEA schedule for 30 common
generics come from the openFDA NDC directory (data/drugs_openfda.json, public domain, fetched by
scripts/fetch_drugs.py). Patients and cases stay SYNTHETIC (seed=7): real prescription records are
protected health data. Prior auth flags are an ASSUMED payer policy, labelled as such in the JSON."""
import json, random
from pathlib import Path
_J = json.loads((Path(__file__).resolve().parent.parent / "data" / "drugs_openfda.json").read_text())
DRUGS = {k: dict(controlled=v["controlled"], pa=v["pa"], dea_schedule=v["dea_schedule"]) for k, v in _J["drugs"].items()}
def make_world(n=300,seed=7):
    r=random.Random(seed); cases=[]
    for i in range(n):
        d=r.choice(list(DRUGS)); refills=r.choice([0,0,1,2,3]); kind=r.choice(["refill","refill","prior_auth"])
        dx=r.random()<0.8; allergy=r.random()<0.05; missing_dob=r.random()<0.06
        cases.append(dict(id=f"C{i}",kind=kind,drug=d,refills_left=refills,has_diagnosis=dx,allergy_flag=allergy,dob=None if missing_dob else "1970-01-01",payer=r.choice(["ODB","SunLife","Manulife"])))
    return cases
def expected(c):
    """Ground truth policy written by hand, independent of the agent code."""
    if c["dob"] is None or c["allergy_flag"] or DRUGS[c["drug"]]["controlled"]: return "escalate_pharmacist"
    if c["kind"]=="refill": return "approve_refill" if c["refills_left"]>0 else "request_prescriber"
    if not DRUGS[c["drug"]]["pa"]: return "no_pa_needed"
    return "submit_pa" if c["has_diagnosis"] else "request_prescriber"
