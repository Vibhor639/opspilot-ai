from uuid import uuid4
from app.services.cost_intelligence import build_cost_summary, detect_cost_anomalies
from app.services.mock_data import INCIDENTS
from app.services.utilization import analyze_utilization

def investigate(question: str):
    costs = build_cost_summary()
    anomalies = detect_cost_anomalies()
    utilization = analyze_utilization()
    open_incidents = [i for i in INCIDENTS if i["status"] != "resolved"]
    findings = [
      {"title":"Overall monthly spend","detail":f"Synthetic data shows ${costs['current_month']:,.2f} this month versus ${costs['previous_month']:,.2f} previously ({costs['change_percent']:.1f}% change).","evidence":["Synthetic service-level monthly cost dataset"]},
      {"title":"Potential cost anomalies","detail":f"Threshold checks identified {len(anomalies)} service-level increase(s).","evidence":[f"{a['service']}: +{a['change_percent']}%" for a in anomalies] or ["No increases met configured thresholds"]},
      {"title":"Resource utilization","detail":f"{utilization['underutilized']} underutilized and {utilization['overutilized']} overutilized resources were found.","evidence":[f"{x['asset_name']}: {x['classification']}" for x in utilization["items"]]},
      {"title":"Open incidents","detail":f"{len(open_incidents)} unresolved incident(s) are in the demo dataset.","evidence":[f"{i['id']}: {i['title']}" for i in open_incidents]},
    ]
    actions = [
      "Validate cost changes against the cloud provider billing export.",
      "Review high-increase services and compare usage, pricing, and deployment changes.",
      "Investigate overutilized resources before considering capacity changes.",
      "Review underutilized resources for rightsizing after checking service requirements.",
      "Correlate open incidents with affected assets before proposing remediation.",
      "Obtain human approval before making any production infrastructure change.",
    ]
    return {"investigation_id":str(uuid4()), "question":question,
      "summary":f"Synthetic data shows a {costs['change_percent']:.1f}% total cost change, {len(anomalies)} cost anomaly candidate(s), and {len(open_incidents)} unresolved incident(s).",
      "findings":findings, "recommended_actions":actions, "requires_human_approval":True,
      "mode":"deterministic_demo",
      "disclaimer":"This is a deterministic demonstration using synthetic data, not a live cloud analysis or forecast. Verify findings with your cloud provider."}
