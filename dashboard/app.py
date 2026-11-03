"""Light mode Streamlit dashboard for the pharmacy agent. Run: streamlit run dashboard/app.py"""
import sys, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import pandas as pd, streamlit as st
from rxagent.tools import make_world, expected
from rxagent.agent import run_case
from rxagent.evaluate import score, noisy_planner

st.set_page_config(page_title="Pharmacy refill and prior auth agent", layout="wide")
st.title("Pharmacy refill and prior auth agent")
st.caption("All cases are synthetic and generated from a fixed seed (seed=7). No real patient data.")

@st.cache_data
def load():
    rows, traces = [], {}
    for c in make_world(300):
        out, tr = run_case(c)
        reason = next((s["why"] for s in tr if s["step"] == "guard"), "")
        rows.append(dict(case=c["id"], kind=c["kind"], drug=c["drug"], payer=c["payer"], refills_left=c["refills_left"],
                         decision=out, expected=expected(c), correct=out == expected(c), escalation_reason=reason))
        traces[c["id"]] = list(tr)
    return pd.DataFrame(rows), traces
df, traces = load()
tab = st.radio("View", ["Case queue", "Audit trail", "Evaluation"], horizontal=True, label_visibility="collapsed")
if tab == "Case queue":
    a, b, c, d = st.columns(4)
    a.metric("Cases", len(df)); b.metric("Correct", int(df.correct.sum()))
    c.metric("Escalated to pharmacist", int((df.decision == "escalate_pharmacist").sum()))
    d.metric("Auto approved refills", int((df.decision == "approve_refill").sum()))
    dec = st.multiselect("Decision", sorted(df.decision.unique()), default=sorted(df.decision.unique()))
    st.dataframe(df[df.decision.isin(dec)], use_container_width=True, hide_index=True, height=520)
elif tab == "Audit trail":
    first = int((df.decision == "escalate_pharmacist").idxmax())
    cid = st.selectbox("Case", df.case.tolist(), index=first)
    r = df[df.case == cid].iloc[0]
    st.markdown(f"**Decision:** `{r.decision}`  |  **Expected:** `{r.expected}`  |  **Escalation reason:** {r.escalation_reason or 'none'}")
    st.dataframe(pd.DataFrame(traces[cid]), use_container_width=True, hide_index=True)
else:
    res = json.loads((ROOT / "results.json").read_text())
    t = pd.DataFrame(res).T.reset_index().rename(columns={"index": "planner"})
    st.dataframe(t, use_container_width=True, hide_index=True)
    st.image(str(ROOT / "docs" / "results_chart.png"))
