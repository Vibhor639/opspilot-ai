# Cloud Billing Reconciliation Runbook

## 1. Purpose

This runbook defines a structured process for reconciling cloud billing data with resource inventories and cost attribution records.

The objective is to identify unexplained expenditure, missing resource mappings, inconsistent billing records, and cost allocation gaps.

## 2. Required investigation data

Collect:

- Billing account and cloud provider
- Billing period and currency
- Service-level cost totals
- Resource-level cost records, where available
- Resource IDs and asset inventory records
- Project, account, and subscription identifiers
- Cost allocation tags and labels
- Credits, discounts, taxes, and adjustments
- Previous billing period totals
- Data extraction timestamps

Confirm that billing and inventory datasets cover compatible time periods.

## 3. Reconciliation procedure

1. Retrieve billing records for the selected period.
2. Retrieve the corresponding cloud asset inventory.
3. Normalize resource identifiers and provider names.
4. Group billing records by service and resource.
5. Match resource-level billing records to inventory entries.
6. Aggregate matched resource costs.
7. Compare matched totals with provider billing totals.
8. Calculate unattributed expenditure.
9. Investigate missing or inconsistent mappings.
10. Document reconciliation results and unresolved differences.

## 4. Cost attribution checks

Check for:

- Resources missing from the asset inventory
- Billing records without resource identifiers
- Missing or inconsistent ownership tags
- Duplicate resource mappings
- Resources moved between accounts or projects
- Shared infrastructure costs
- Credits and discounts not assigned to individual resources
- Differences in billing period boundaries

Do not assign unattributed expenditure to individual resources without supporting evidence.

## 5. Variance analysis

For each service and resource, calculate:

- Current period cost
- Previous period cost
- Absolute cost difference
- Percentage cost difference

Investigate material increases and decreases.

A variance may result from workload changes, pricing changes, credits, usage changes, or incomplete data.

## 6. Reconciliation output

Record:

- Billing period and currency
- Provider billing total
- Total attributed resource cost
- Unattributed cost
- Reconciliation difference
- Service-level cost breakdown
- Top cost increases
- Missing resource mappings
- Suspected causes
- Recommended follow-up actions
- Data extraction timestamps

## 7. Production and financial controls

- Preserve original billing records.
- Record reconciliation timestamps and data sources.
- Avoid modifying source billing data.
- Document assumptions and calculation methods.
- Obtain finance or cloud-owner review for material discrepancies.
- Do not treat estimated costs as final invoice amounts.
- Follow organizational financial reporting procedures.

## 8. Important limitations

Billing datasets may differ in granularity, currency, timing, and treatment of discounts or shared costs.

Resource-level attribution may not equal the provider's invoice total.

All discrepancies must be investigated using authoritative billing records before financial reporting or cost adjustments.

This runbook provides operational guidance and does not authorize financial or infrastructure changes.
