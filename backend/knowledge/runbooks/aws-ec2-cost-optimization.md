# AWS EC2 Cost Optimization and Rightsizing Runbook

## 1. Purpose

This runbook provides a controlled procedure for investigating AWS EC2 cost increases and identifying potential rightsizing opportunities.

The objective is to reduce unnecessary cloud expenditure without compromising availability, reliability, security, or application performance.

## 2. Required investigation data

Collect the following information for each EC2 instance:

- Instance ID and instance name
- AWS account and region
- Instance type and pricing model
- Current and previous billing period costs
- CPU utilization averages and peaks
- Memory utilization averages and peaks
- Network throughput
- Disk I/O and storage utilization
- Environment and owner team
- Application criticality
- Associated production incidents

Use AWS Cost Explorer, AWS Compute Optimizer, CloudWatch and the organization's asset inventory as appropriate.

## 3. Cost increase investigation

1. Compare current and previous billing periods.
2. Identify services and resources with the largest absolute cost increases.
3. Calculate percentage changes.
4. Check whether instance types, running hours, storage, or data transfer changed.
5. Investigate unexpected scaling activity and workload changes.
6. Validate billing data against the asset inventory.

A percentage increase alone does not establish that a resource is wasteful.

## 4. Rightsizing assessment

Use these guidelines as initial screening criteria, not automatic resizing rules.

### Potentially underutilized

Investigate instances with:

- Sustained CPU utilization below 20%.
- Sustained memory utilization below 35%.

Before recommending a change, inspect peak utilization, workload schedules, memory requirements, network activity, and application behavior.

### Potentially overutilized

Investigate instances with:

- Sustained CPU utilization above 85%.
- Memory utilization above 90%.

Check for saturation, performance degradation, increased latency, and capacity constraints.

Do not automatically downsize an overutilized instance.

## 5. Recommended investigation procedure

1. Identify the highest-cost increases.
2. Correlate cost changes with CPU and memory utilization.
3. Identify low-utilization resources with rising costs.
4. Check whether the workload is seasonal or scheduled.
5. Compare alternative instance types and pricing models.
6. Estimate potential savings using verified pricing information.
7. Review application performance and availability requirements.
8. Document findings and supporting evidence.

## 6. Production safety requirements

Before any infrastructure change:

- Obtain application-owner approval.
- Follow the organization's change-management process.
- Verify backup and recovery arrangements.
- Review availability-zone and redundancy requirements.
- Define rollback procedures.
- Schedule changes within an approved maintenance window.
- Monitor performance after implementation.

No resizing, stopping, or termination should occur solely on the basis of an automated recommendation.

## 7. Investigation output

Document:

- Resource ID and name
- Current and previous monthly cost
- Absolute and percentage cost change
- CPU and memory utilization
- Potential optimization opportunity
- Business and operational risks
- Supporting evidence
- Recommended next steps
- Required approvals

## 8. Important limitations

Cost and utilization recommendations must be validated against current provider telemetry and billing records.

Historical averages may hide peak demand or scheduled workloads.

This runbook provides operational guidance and does not authorize infrastructure changes.
