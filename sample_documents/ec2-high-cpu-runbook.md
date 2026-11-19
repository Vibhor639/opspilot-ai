# EC2 High CPU Utilization Runbook

## Purpose
This runbook describes a safe investigation process for sustained high CPU utilization on an EC2 instance.

## Initial checks
1. Confirm the affected instance ID, AWS region, environment, and owning team.
2. Review CPU utilization over the last 15 to 60 minutes in CloudWatch.
3. Check whether the increase aligns with a deployment, scheduled job, traffic spike, or batch process.
4. Review memory, disk I/O, network throughput, and application latency alongside CPU.

## Investigation
- Compare current CPU metrics with the same time window from the previous day or week.
- Inspect application and system logs for repeated errors, retry loops, or unexpectedly frequent jobs.
- Check whether autoscaling policies and desired capacity are behaving as expected.
- Correlate the instance with open incidents and recent change records.

## Remediation options
- If traffic has increased and the workload is healthy, evaluate scaling out through the approved autoscaling policy.
- If a runaway process is identified, follow the service owner's incident procedure before restarting or terminating it.
- If the instance is consistently undersized, propose a rightsizing change with performance evidence.
- Do not stop, resize, or terminate a production instance without approval from the service owner and change-management process.

## Verification
1. Confirm CPU utilization returns to the expected range.
2. Verify application latency and error rates have not worsened.
3. Record the root cause, evidence, action, approver, and outcome in the incident record.

## Escalation
Escalate to the service owner and cloud operations team if customer impact is observed, the cause is unclear, or the issue persists after approved remediation.
