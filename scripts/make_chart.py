"""Build docs/results_chart.png from results.json (real evaluation output)."""
import json, pathlib
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = pathlib.Path(__file__).resolve().parents[1]; res = json.loads((R / "results.json").read_text())
k = ["stub_planner_first_100_cases", "qwen2.5-3b_planner_first_100_cases"]; names = ["Deterministic planner", "Qwen2.5 3B planner"]
fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
for a, (m, title) in zip(ax, [("correct", "Correct of 100"), ("escalated", "Escalated to pharmacist"), ("unsafe_auto_actions", "Unsafe auto approvals")]):
    v = [res[x][m] for x in k]; bars = a.bar(names, v, color=["#2b6cb0", "#dd8a2b"])
    a.set_title(title); a.set_ylim(0, max(110 if m != "unsafe_auto_actions" else 1, max(v) * 1.2)); a.tick_params(axis="x", labelsize=8)
    for b_, val in zip(bars, v): a.text(b_.get_x() + b_.get_width() / 2, b_.get_height(), str(val), ha="center", va="bottom")
fig.suptitle("First 100 cases: real openFDA drug facts, synthetic patients"); fig.tight_layout(); fig.savefig(R / "docs" / "results_chart.png", dpi=130)
