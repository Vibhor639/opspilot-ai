
from app.services.mock_data import MONTHLY_COSTS, ASSETS


def percentage_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 2)


def build_cost_summary():
    services = []

    for item in MONTHLY_COSTS:
        current = item["current_month"]
        previous = item["previous_month"]

        services.append({
            **item,
            "change_amount": round(current - previous, 2),
            "change_percent": percentage_change(current, previous),
        })

    current_total = round(sum(x["current_month"] for x in MONTHLY_COSTS), 2)
    previous_total = round(sum(x["previous_month"] for x in MONTHLY_COSTS), 2)

    return {
        "currency": "USD",
        "current_month": current_total,
        "previous_month": previous_total,
        "change_amount": round(current_total - previous_total, 2),
        "change_percent": percentage_change(current_total, previous_total),
        "services": services,
    }


def build_resource_cost_attribution():
    """Attribute tracked cloud costs to individual synthetic resources."""

    resources = []

    for asset in ASSETS:
        current = float(asset["monthly_cost"])
        previous = float(asset["previous_monthly_cost"])
        change = round(current - previous, 2)

        resources.append({
            "asset_id": asset["id"],
            "asset_name": asset["name"],
            "provider": asset["provider"],
            "resource_type": asset["resource_type"],
            "region": asset["region"],
            "environment": asset["environment"],
            "owner_team": asset["owner_team"],
            "current_month": round(current, 2),
            "previous_month": round(previous, 2),
            "change_amount": change,
            "change_percent": percentage_change(current, previous),
            "cpu_utilization_percent": asset["cpu_utilization_percent"],
            "memory_utilization_percent": asset["memory_utilization_percent"],
        })

    resources.sort(key=lambda item: item["change_amount"], reverse=True)

    tracked_current = round(sum(item["current_month"] for item in resources), 2)
    tracked_previous = round(sum(item["previous_month"] for item in resources), 2)

    service_summary = build_cost_summary()
    total_current = service_summary["current_month"]
    total_previous = service_summary["previous_month"]

    unattributed_current = round(total_current - tracked_current, 2)
    unattributed_previous = round(total_previous - tracked_previous, 2)

    return {
        "currency": "USD",
        "tracked_resource_count": len(resources),
        "tracked_current_month": tracked_current,
        "tracked_previous_month": tracked_previous,
        "tracked_change_amount": round(tracked_current - tracked_previous, 2),
        "tracked_change_percent": percentage_change(tracked_current, tracked_previous),
        "unattributed_current_month": unattributed_current,
        "unattributed_previous_month": unattributed_previous,
        "unattributed_change_amount": round(
            unattributed_current - unattributed_previous, 2
        ),
        "total_current_month": total_current,
        "total_previous_month": total_previous,
        "total_change_amount": service_summary["change_amount"],
        "resources": resources,
        "top_cost_increases": [
            item for item in resources if item["change_amount"] > 0
        ][:3],
    }


def detect_cost_anomalies(
    min_change_percent: float = 20.0,
    min_change_amount: float = 50.0,
):
    flagged = []

    for item in MONTHLY_COSTS:
        current = item["current_month"]
        previous = item["previous_month"]
        amount = round(current - previous, 2)
        pct = percentage_change(current, previous)

        if amount >= min_change_amount and pct >= min_change_percent:
            flagged.append({
                "service": item["service"],
                "current_month": current,
                "previous_month": previous,
                "change_amount": amount,
                "change_percent": pct,
                "severity": "high" if pct >= 40 else "medium",
                "explanation": (
                    f"{item['service']} spend increased by "
                    f"${amount:,.2f} ({pct:.1f}%) compared with the previous month."
                ),
            })

    return sorted(flagged, key=lambda x: x["change_amount"], reverse=True)
