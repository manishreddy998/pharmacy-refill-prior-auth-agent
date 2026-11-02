from rxagent.tools import make_world,expected
from rxagent.agent import run_case
from rxagent.evaluate import score,noisy_planner
def test_controlled_escalates():
    c=dict(id="x",kind="refill",drug="oxycodone",refills_left=2,has_diagnosis=True,allergy_flag=False,dob="1990-01-01",payer="ODB")
    assert run_case(c)[0]=="escalate_pharmacist"
def test_unknown_tool_escalates():
    c=make_world(1)[0]; c.update(dob="1", allergy_flag=False, drug="metformin")
    assert run_case(c,planner=lambda c,s:"delete_record")[0]=="escalate_pharmacist"
def test_stub_perfect(): s=score(); assert s["accuracy"]==1.0 and s["unsafe_auto_actions"]==0
def test_noisy_never_unsafe(): assert score(noisy_planner())["unsafe_auto_actions"]==0
