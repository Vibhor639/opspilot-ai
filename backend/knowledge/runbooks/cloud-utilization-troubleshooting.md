# Cloud Resource Utilization Troubleshooting Runbook

## 1. Purpose

This runbook provides a consistent process for investigating abnormal CPU, memory, network, and storage utilization across cloud resources.

The objective is to identify capacity risks, performance bottlenecks, and potential resource inefficiencies without making unsafe infrastructure changes.

## 2. Required investigation data

Collect the following information:

- Resource ID, name, and resource type
- Cloud provider, account, and region
- Environment and owner team
- CPU utilization averages, peaks, and trends
- Memory utilization averages, peaks, and trends
- Network throughput and packet metrics
- Disk I/O, latency, and storage utilization
- Application response times and error rates
- Recent deployments and configuration changes
- Related incidents and alerts

Use available provider monitoring tools and application telemetry.

## 3. CPU utilization investigation

### High CPU utilization

Investigate sustained CPU utilization above 85%.

1. Identify the affected resource and workload.
2. Check CPU trends and peak periods.
3. Correlate utilization with application latency and error rates.
4. Review recent deployments and traffic changes.
5. Check for unexpected background processes.
6. Assess whether capacity expansion or workload optimization is required.

### Low CPU utilization

Investigate sustained CPU utilization below 20%.

1. Check whether the workload is scheduled or intermittent.
2. Review peak utilization and historical trends.
3. Verify application criticality and availability requirements.
4. Compare resource size with actual workload demand.
5. Identify potential rightsizing opportunities.

Low CPU utilization alone is not sufficient evidence to downsize a resource.

## 4. Memory utilization investigation

Investigate sustained memory utilization above 90%.

1. Review memory usage trends.
2. Check for memory leaks or abnormal processes.
3. Correlate memory pressure with application performance.
4. Review recent application and configuration changes.
5. Determine whether additional capacity or application optimization is needed.

Memory utilization below 35% may indicate an optimization opportunity, but workload peaks and minimum application requirements must be considered.

## 5. Network and storage investigation

For network-related anomalies:

- Review inbound and outbound traffic trends.
- Identify unexpected traffic increases.
- Check network latency and packet drops.
- Correlate traffic with application activity.

For storage-related anomalies:

- Review disk capacity and growth.
- Inspect read/write throughput and latency.
- Check for unexpected storage consumption.
- Review backup, retention, and data lifecycle policies.

## 6. Troubleshooting workflow

1. Identify the affected resource.
2. Establish the time window of the anomaly.
3. Collect CPU, memory, network, and storage metrics.
4. Compare current behavior with historical baselines.
5. Correlate metrics with deployments and incidents.
6. Identify likely contributing factors.
7. Document evidence and operational impact.
8. Recommend corrective actions.
9. Obtain required approvals before production changes.
10. Monitor the resource after an approved change.

## 7. Production safety requirements

- Do not resize or restart production resources automatically.
- Verify redundancy and failover arrangements.
- Check application-owner requirements.
- Follow change-management procedures.
- Define rollback and recovery steps.
- Monitor service health after approved changes.

## 8. Investigation output

Record:

- Resource ID and name
- Anomaly type and time window
- Observed metric values
- Historical baseline
- Related deployments or incidents
- Suspected contributing factors
- Business and operational impact
- Recommended corrective action
- Required approvals

## 9. Important limitations

Thresholds in this runbook are initial investigation indicators, not universal performance limits.

Recommendations must be validated against workload characteristics, provider telemetry, and organization-specific operating requirements.

This runbook provides guidance and does not authorize infrastructure changes.
