"""Read-only live AWS/GCP integrations with explicit configuration checks.

Credentials are obtained only through the standard provider credential chains:
AWS environment/shared config/instance roles and Google Application Default Credentials.
No credentials are accepted in API request bodies or returned in responses.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone, date
from typing import Any


class CloudProviderError(RuntimeError):
    """Safe, user-facing cloud integration error."""


def _mode() -> str:
    return os.getenv("CLOUD_MODE", "demo").strip().lower()


def get_cloud_connection_status() -> dict[str, Any]:
    """Report configuration presence without exposing secrets or probing APIs."""
    return {
        "mode": _mode(),
        "aws": {
            "configured": bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE") or os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE")),
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "credential_source": "standard AWS credential chain",
        },
        "gcp": {
            "configured": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GCP_PROJECT_ID")),
            "project_id_configured": bool(os.getenv("GCP_PROJECT_ID")),
            "billing_export_configured": all(os.getenv(k) for k in ("GCP_BILLING_PROJECT", "GCP_BILLING_DATASET", "GCP_BILLING_TABLE")),
            "credential_source": "Google Application Default Credentials",
        },
        "safety": "Read-only discovery and monitoring. No infrastructure changes are performed.",
    }


def _require_live() -> None:
    if _mode() != "live":
        raise CloudProviderError("Live cloud access is disabled. Set CLOUD_MODE=live in backend/.env and restart the services.")


def _aws_client(service: str, region: str | None = None):
    _require_live()
    try:
        import boto3
        return boto3.client(service, region_name=region or os.getenv("AWS_REGION", "us-east-1"))
    except ImportError as exc:
        raise CloudProviderError("AWS SDK is missing. Install requirements.txt again.") from exc
    except Exception as exc:
        raise CloudProviderError(f"Could not initialize AWS {service} client: {exc}") from exc


def _gcp_project(project_id: str | None = None) -> str:
    _require_live()
    project = project_id or os.getenv("GCP_PROJECT_ID")
    if not project:
        raise CloudProviderError("GCP_PROJECT_ID is not configured in backend/.env.")
    return project


def list_live_cloud_assets(provider: str, project_id: str | None = None, region: str | None = None) -> dict[str, Any]:
    provider = provider.upper()
    if provider == "AWS":
        ec2 = _aws_client("ec2", region)
        try:
            response = ec2.describe_instances()
            assets = []
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    tags = {t.get("Key", ""): t.get("Value", "") for t in instance.get("Tags", [])}
                    assets.append({
                        "id": instance.get("InstanceId"),
                        "name": tags.get("Name", instance.get("InstanceId", "EC2 instance")),
                        "provider": "AWS", "resource_type": "EC2",
                        "region": region or os.getenv("AWS_REGION", "us-east-1"),
                        "state": instance.get("State", {}).get("Name", "unknown"),
                        "instance_type": instance.get("InstanceType"),
                        "private_ip": instance.get("PrivateIpAddress"),
                        "launch_time": instance.get("LaunchTime").isoformat() if instance.get("LaunchTime") else None,
                        "tags": tags,
                    })
            return {"source": "aws_live", "count": len(assets), "assets": assets}
        except Exception as exc:
            raise CloudProviderError(f"AWS EC2 inventory failed: {exc}") from exc
    if provider == "GCP":
        project = _gcp_project(project_id)
        try:
            from google.cloud import compute_v1
            client = compute_v1.InstancesClient()
            assets = []
            for scope, scoped_list in client.aggregated_list(project=project):
                for instance in scoped_list.instances or []:
                    zone = (instance.zone or "").split("/")[-1]
                    assets.append({
                        "id": str(instance.id), "name": instance.name,
                        "provider": "GCP", "resource_type": "Compute Engine",
                        "region": zone, "state": (instance.status or "UNKNOWN").lower(),
                        "machine_type": (instance.machine_type or "").split("/")[-1],
                        "private_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
                        "creation_timestamp": instance.creation_timestamp,
                        "labels": dict(instance.labels or {}),
                    })
            return {"source": "gcp_live", "project_id": project, "count": len(assets), "assets": assets}
        except ImportError as exc:
            raise CloudProviderError("Google Compute SDK is missing. Install requirements.txt again.") from exc
        except Exception as exc:
            raise CloudProviderError(f"GCP Compute Engine inventory failed: {exc}") from exc
    raise CloudProviderError("provider must be AWS or GCP.")


def get_live_compute_metrics(provider: str, resource_id: str, lookback_minutes: int = 60, region: str | None = None, project_id: str | None = None) -> dict[str, Any]:
    if not resource_id.strip():
        raise CloudProviderError("resource_id is required.")
    if not 5 <= lookback_minutes <= 1440:
        raise CloudProviderError("lookback_minutes must be between 5 and 1440.")
    provider = provider.upper()
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=lookback_minutes)
    if provider == "AWS":
        client = _aws_client("cloudwatch", region)
        try:
            response = client.get_metric_statistics(
                Namespace="AWS/EC2", MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": resource_id}],
                StartTime=start, EndTime=end, Period=300, Statistics=["Average", "Maximum"],
            )
            points = sorted(response.get("Datapoints", []), key=lambda x: x["Timestamp"])
            return {"source": "aws_cloudwatch_live", "provider": "AWS", "resource_id": resource_id,
                    "metric": "CPUUtilization", "unit": "Percent", "lookback_minutes": lookback_minutes,
                    "datapoints": [{"timestamp": p["Timestamp"].isoformat(), "average": p.get("Average"), "maximum": p.get("Maximum")} for p in points]}
        except Exception as exc:
            raise CloudProviderError(f"AWS CloudWatch metric query failed: {exc}") from exc
    if provider == "GCP":
        project = _gcp_project(project_id)
        if not re.fullmatch(r"[0-9]+", resource_id):
            raise CloudProviderError("For GCP, resource_id must be the numeric Compute Engine instance ID.")
        try:
            from google.cloud import monitoring_v3
            client = monitoring_v3.MetricServiceClient()
            interval = monitoring_v3.TimeInterval(
                end_time={"seconds": int(end.timestamp())},
                start_time={"seconds": int(start.timestamp())},
            )
            results = client.list_time_series(
                request={"name": f"projects/{project}",
                         "filter": f'metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.labels.instance_id="{resource_id}"',
                         "interval": interval, "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL},
                timeout=30,
            )
            points = []
            for series in results:
                for point in series.points:
                    value = point.value.double_value if point.value.HasField("double_value") else None
                    end_time = point.interval.end_time
                    if hasattr(end_time, "ToDatetime"):
                        end_time = end_time.ToDatetime(timezone=timezone.utc)
                    points.append({"timestamp": end_time.isoformat(), "utilization_fraction": value,
                                   "utilization_percent": round(value * 100, 2) if value is not None else None})
            return {"source": "gcp_monitoring_live", "provider": "GCP", "resource_id": resource_id,
                    "metric": "compute.googleapis.com/instance/cpu/utilization", "lookback_minutes": lookback_minutes,
                    "datapoints": points}
        except ImportError as exc:
            raise CloudProviderError("Google Cloud Monitoring SDK is missing. Install requirements.txt again.") from exc
        except Exception as exc:
            raise CloudProviderError(f"GCP Monitoring metric query failed: {exc}") from exc
    raise CloudProviderError("provider must be AWS or GCP.")


def get_live_cost_summary(provider: str, start_date: str, end_date: str, region: str | None = None, project_id: str | None = None) -> dict[str, Any]:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as exc:
        raise CloudProviderError("Dates must use YYYY-MM-DD format.") from exc
    if end <= start:
        raise CloudProviderError("end_date must be later than start_date.")
    provider = provider.upper()
    if provider == "AWS":
        client = _aws_client("ce", region or "us-east-1")
        try:
            response = client.get_cost_and_usage(
                TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
                Granularity="MONTHLY", Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
            groups = []
            for period in response.get("ResultsByTime", []):
                for group in period.get("Groups", []):
                    amount = group.get("Metrics", {}).get("UnblendedCost", {})
                    groups.append({"period_start": period.get("TimePeriod", {}).get("Start"),
                                   "service": group.get("Keys", ["Unknown"])[0],
                                   "amount": float(amount.get("Amount", 0)), "currency": amount.get("Unit", "USD")})
            return {"source": "aws_cost_explorer_live", "provider": "AWS", "start_date": start_date,
                    "end_date_exclusive": end_date.isoformat(), "groups": groups}
        except Exception as exc:
            raise CloudProviderError(f"AWS Cost Explorer query failed: {exc}") from exc
    if provider == "GCP":
        project = _gcp_project(project_id)
        billing_project = os.getenv("GCP_BILLING_PROJECT", project)
        dataset, table = os.getenv("GCP_BILLING_DATASET", ""), os.getenv("GCP_BILLING_TABLE", "")
        if (not dataset or not table or not re.fullmatch(r"[A-Za-z0-9_-]+", billing_project)
                or not re.fullmatch(r"[A-Za-z0-9_]+", dataset) or not re.fullmatch(r"[A-Za-z0-9_]+", table)):
            raise CloudProviderError("Configure GCP_BILLING_DATASET and GCP_BILLING_TABLE for a BigQuery billing export. GCP billing is not available from Compute Engine metrics alone.")
        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=billing_project)
            table_ref = f"`{billing_project}.{dataset}.{table}`"
            query = f"""SELECT service.description AS service, currency, SUM(cost) AS amount
                       FROM {table_ref}
                       WHERE DATE(usage_start_time) >= @start_date AND DATE(usage_start_time) < @end_date
                       GROUP BY service, currency ORDER BY amount DESC"""
            config = bigquery.QueryJobConfig(query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start),
                bigquery.ScalarQueryParameter("end_date", "DATE", end),
            ])
            rows = client.query(query, job_config=config).result(timeout=60)
            groups = [{"service": row.service, "currency": row.currency, "amount": float(row.amount)} for row in rows]
            return {"source": "gcp_billing_export_bigquery_live", "provider": "GCP", "project_id": project,
                    "start_date": start_date, "end_date_exclusive": end.isoformat(), "groups": groups}
        except ImportError as exc:
            raise CloudProviderError("Google BigQuery SDK is missing. Install requirements.txt again.") from exc
        except Exception as exc:
            raise CloudProviderError(f"GCP BigQuery billing query failed: {exc}") from exc
    raise CloudProviderError("provider must be AWS or GCP.")
