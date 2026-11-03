"""Fetch REAL drug facts from openFDA NDC directory (api.fda.gov/drug/ndc.json, US public domain / CC0).
For each generic name we keep: whether any listed product has a DEA schedule (controlled), the
schedule, and the number of NDC products found. Saved to data/drugs_openfda.json."""
import json, time, urllib.request, urllib.parse
from pathlib import Path
# 30 commonly dispensed generics (my list). PA flags below are an ASSUMED payer policy, not real.
PA_ASSUMED = {"semaglutide", "adalimumab", "apixaban", "rivaroxaban", "dulaglutide", "etanercept", "insulin glargine", "empagliflozin", "sitagliptin", "ustekinumab"}
NAMES = ["atorvastatin", "metformin", "semaglutide", "adalimumab", "oxycodone", "lisinopril", "apixaban", "amlodipine", "levothyroxine",
         "sertraline", "alprazolam", "lorazepam", "zolpidem", "tramadol", "hydrocodone", "methylphenidate", "amphetamine", "gabapentin",
         "pregabalin", "rivaroxaban", "dulaglutide", "etanercept", "insulin glargine", "empagliflozin", "sitagliptin", "ustekinumab",
         "omeprazole", "rosuvastatin", "clonazepam", "buprenorphine"]
out = {}
for n in NAMES:
    q = urllib.parse.quote(f'generic_name:"{n}"')
    for attempt in range(3):
        try:
            r = json.loads(urllib.request.urlopen(f"https://api.fda.gov/drug/ndc.json?search={q}&limit=100", timeout=30).read())["results"]; break
        except Exception as e:
            r = []; time.sleep(2)
    sched = sorted({x["dea_schedule"] for x in r if x.get("dea_schedule")})
    out[n] = {"controlled": bool(sched), "dea_schedule": sched, "ndc_products_seen": len(r), "pa": n in PA_ASSUMED, "pa_source": "ASSUMED"}
    time.sleep(0.3)
Path("data/drugs_openfda.json").write_text(json.dumps({"source": "openFDA NDC directory", "fetched": time.strftime("%Y-%m-%d"), "drugs": out}, indent=1))
print({k: v["dea_schedule"] for k, v in out.items() if v["controlled"]}, sum(v["ndc_products_seen"] == 0 for v in out.values()))
