"""Fake but realistic pharmacy back end: patients, prescriptions, payer formulary rules."""
import random
DRUGS={"atorvastatin":dict(controlled=False,pa=False),"metformin":dict(controlled=False,pa=False),"semaglutide":dict(controlled=False,pa=True),
 "adalimumab":dict(controlled=False,pa=True),"oxycodone":dict(controlled=True,pa=False),"lisinopril":dict(controlled=False,pa=False),"apixaban":dict(controlled=False,pa=True)}
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
