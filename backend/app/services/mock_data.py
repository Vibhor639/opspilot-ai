# Synthetic development data only; not live cloud telemetry or billing data.
ASSETS = [
 {"id":"i-ops-001","name":"payments-api-prod","provider":"AWS","resource_type":"EC2","region":"ap-south-1","monthly_cost":420.0,"previous_monthly_cost":330.0,"cpu_utilization_percent":72.0,"memory_utilization_percent":68.0,"environment":"production","owner_team":"payments","tags":{"application":"payments","criticality":"high"}},
 {"id":"i-ops-002","name":"analytics-worker-prod","provider":"AWS","resource_type":"EC2","region":"ap-south-1","monthly_cost":310.0,"previous_monthly_cost":240.0,"cpu_utilization_percent":12.0,"memory_utilization_percent":28.0,"environment":"production","owner_team":"data-platform","tags":{"application":"analytics","criticality":"medium"}},
 {"id":"gcp-ops-003","name":"reporting-cluster","provider":"GCP","resource_type":"GKE","region":"asia-south1","monthly_cost":275.0,"previous_monthly_cost":260.0,"cpu_utilization_percent":91.0,"memory_utilization_percent":93.0,"environment":"production","owner_team":"reporting","tags":{"application":"reporting","criticality":"high"}},
 {"id":"i-ops-004","name":"dev-sandbox","provider":"AWS","resource_type":"EC2","region":"ap-south-1","monthly_cost":95.0,"previous_monthly_cost":90.0,"cpu_utilization_percent":8.0,"memory_utilization_percent":16.0,"environment":"development","owner_team":"developer-experience","tags":{"application":"sandbox","criticality":"low"}},
 {"id":"gcp-ops-005","name":"customer-db","provider":"GCP","resource_type":"Cloud SQL","region":"asia-south1","monthly_cost":460.0,"previous_monthly_cost":430.0,"cpu_utilization_percent":54.0,"memory_utilization_percent":61.0,"environment":"production","owner_team":"database","tags":{"application":"customer-platform","criticality":"critical"}},
]
MONTHLY_COSTS = [
 {"service":"EC2","current_month":1180.0,"previous_month":850.0},
 {"service":"RDS","current_month":460.0,"previous_month":430.0},
 {"service":"S3","current_month":120.0,"previous_month":115.0},
 {"service":"EKS/GKE","current_month":275.0,"previous_month":260.0},
]
INCIDENTS = [
 {"id":"INC-1042","title":"Elevated latency on payments API","severity":"high","status":"investigating","affected_asset_ids":["i-ops-001"]},
 {"id":"INC-1048","title":"Analytics worker CPU saturation","severity":"medium","status":"open","affected_asset_ids":["i-ops-002"]},
 {"id":"INC-1051","title":"Reporting cluster memory pressure","severity":"high","status":"open","affected_asset_ids":["gcp-ops-003"]},
]
