from app.services.mock_data import ASSETS

def classify_asset(asset: dict):
    cpu, memory = asset["cpu_utilization_percent"], asset["memory_utilization_percent"]
    if cpu >= 85 or memory >= 90:
        label = "overutilized"
        advice = "Investigate workload demand, saturation, and scaling limits. Review before changing production capacity."
    elif cpu < 20 and memory < 35:
        label = "underutilized"
        advice = "Review workload patterns and rightsizing opportunities; verify service requirements before downsizing."
    else:
        label = "healthy"
        advice = "Continue monitoring CPU and memory utilization."
    return {"asset_id":asset["id"], "asset_name":asset["name"], "resource_type":asset["resource_type"],
            "cpu_utilization_percent":cpu, "memory_utilization_percent":memory,
            "classification":label, "recommendation":advice}

def analyze_utilization(classification=None):
    items = [classify_asset(a) for a in ASSETS]
    if classification:
        items = [x for x in items if x["classification"] == classification]
    return {"total_assets":len(items),
            "underutilized":sum(x["classification"]=="underutilized" for x in items),
            "healthy":sum(x["classification"]=="healthy" for x in items),
            "overutilized":sum(x["classification"]=="overutilized" for x in items),
            "items":items}
