
import { useMemo } from 'react'
import {
  Activity, AlertTriangle, ArrowUpRight,
  DollarSign, TrendingUp, TrendingDown, Server, Lightbulb,
  RefreshCw, Info, Gauge,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import type {
  Asset, CostSummary, CostAnomaly,
} from '../services/api'
import './CostIntelligence.css'

interface CostIntelligenceProps {
  costSummary: CostSummary | null
  costAnomalies: CostAnomaly[]
  assets: Asset[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

function money(value: number, currency = 'USD') {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(value)
  } catch {
    return `${currency} ${value.toLocaleString()}`
  }
}

function percentage(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function CostIntelligence({
  costSummary,
  costAnomalies,
  assets,
  loading,
  error,
  onRefresh,
}: CostIntelligenceProps) {
  const currency = costSummary?.currency || 'USD'

  const inventoryCost = useMemo(
    () => assets.reduce((total, asset) => total + asset.monthly_cost, 0),
    [assets],
  )

  const billingCost = costSummary?.current_month ?? 0
  const billingPrevious = costSummary?.previous_month ?? 0
  const billingDifference = billingCost - inventoryCost
  const reconciliationPercent = billingCost > 0
    ? (billingDifference / billingCost) * 100
    : 0

  const services = costSummary?.services ?? []

  const chartData = services.map(service => ({
    service: service.service,
    current: service.current_month,
    previous: service.previous_month,
  }))

  const sortedServices = [...services].sort(
    (a, b) => b.current_month - a.current_month,
  )

  const optimizationCandidates = assets
    .filter(asset =>
      asset.cpu_utilization_percent < 20 &&
      asset.memory_utilization_percent < 30,
    )
    .sort((a, b) => b.monthly_cost - a.monthly_cost)

  const potentialSavings = optimizationCandidates.reduce(
    (total, asset) => total + asset.monthly_cost,
    0,
  )

  const hasCostData = costSummary !== null

  return (
    <section className="cost-intelligence-page">
      <div className="cost-page-heading">
        <div>
          <div className="eyebrow">FINOPS / CLOUD SPEND MANAGEMENT</div>
          <h1>Cost intelligence</h1>
          <p>Understand cloud expenditure, identify anomalies and discover optimization opportunities.</p>
        </div>

        <button
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw size={15} className={loading ? 'cost-spin' : ''} />
          Refresh data
        </button>
      </div>

      {error && (
        <div className="cost-error">
          <AlertTriangle size={17} />
          <span>{error}</span>
          <button onClick={onRefresh}>Retry</button>
        </div>
      )}

      {!hasCostData && loading ? (
        <div className="cost-loading">
          <RefreshCw size={19} className="cost-spin" />
          Loading cost intelligence data...
        </div>
      ) : !hasCostData ? (
        <div className="cost-empty">
          <DollarSign size={25} />
          <strong>Cost data unavailable</strong>
          <span>Check your backend connection and refresh the data.</span>
        </div>
      ) : (
        <>
          <div className="cost-demo-notice">
            <Info size={16} />
            <span>
              <strong>Demo billing data:</strong> Figures are supplied by the
              backend cost summary API and are not connected to live cloud billing accounts.
            </span>
          </div>

          <div className="cost-metric-grid">
            <CostMetric
              label="Current month spend"
              value={money(billingCost, currency)}
              caption="Total reported cloud billing"
              icon={<DollarSign size={19} />}
            />

            <CostMetric
              label="Previous month spend"
              value={money(billingPrevious, currency)}
              caption="Previous billing period"
              icon={<Activity size={19} />}
            />

            <CostMetric
              label="Month-over-month change"
              value={percentage(costSummary.change_percent)}
              caption={`${money(costSummary.change_amount, currency)} change`}
              icon={
                costSummary.change_amount >= 0
                  ? <TrendingUp size={19} />
                  : <TrendingDown size={19} />
              }
              tone={costSummary.change_amount > 0 ? 'warning' : 'positive'}
            />

            <CostMetric
              label="Inventoried resource spend"
              value={money(inventoryCost, currency)}
              caption={`${assets.length} resources in inventory`}
              icon={<Server size={19} />}
            />
          </div>

          <div className="cost-main-grid">
            <section className="cost-panel">
              <div className="cost-panel-heading">
                <div>
                  <h2>Service-level expenditure</h2>
                  <p>Current and previous month by service</p>
                </div>
                <span className="cost-api-label">API DATA</span>
              </div>

              {chartData.length > 0 ? (
                <div className="cost-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      margin={{ top: 10, right: 8, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid
                        stroke="#263348"
                        strokeDasharray="3 4"
                        vertical={false}
                      />
                      <XAxis
                        dataKey="service"
                        tick={{ fill: '#91a0b6', fontSize: 10 }}
                        axisLine={{ stroke: '#263348' }}
                        tickLine={false}
                      />
                      <YAxis
                        tick={{ fill: '#91a0b6', fontSize: 10 }}
                        axisLine={false}
                        tickLine={false}
                        width={65}
                      />
                      <Tooltip
                        contentStyle={{
                          background: '#111a29',
                          border: '1px solid #303b50',
                          borderRadius: 8,
                          color: '#e5eaf3',
                          fontSize: 11,
                        }}
                        formatter={(value) => money(Number(value), currency)}
                      />
                      <Legend
                        wrapperStyle={{
                          fontSize: 10,
                          color: '#91a0b6',
                        }}
                      />
                      <Bar
                        dataKey="previous"
                        name="Previous month"
                        fill="#56647d"
                        radius={[4, 4, 0, 0]}
                      />
                      <Bar
                        dataKey="current"
                        name="Current month"
                        fill="#8b82f6"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="cost-empty">No service-level data returned.</div>
              )}
            </section>

            <section className="cost-panel">
              <div className="cost-panel-heading">
                <div>
                  <h2>Service cost breakdown</h2>
                  <p>Ranked by current month expenditure</p>
                </div>
                <span className="cost-api-label">API DATA</span>
              </div>

              <div className="service-cost-list">
                {sortedServices.map(service => {
                  const share = billingCost > 0
                    ? (service.current_month / billingCost) * 100
                    : 0

                  return (
                    <div className="service-cost-item" key={service.service}>
                      <div className="service-cost-top">
                        <strong>{service.service}</strong>
                        <strong>{money(service.current_month, currency)}</strong>
                      </div>
                      <div className="service-cost-track">
                        <div
                          className="service-cost-fill"
                          style={{ width: `${Math.min(100, share)}%` }}
                        />
                      </div>
                      <div className="service-cost-bottom">
                        <span>{share.toFixed(1)}% of reported billing</span>
                        <span className={service.change_amount > 0 ? 'cost-increase' : 'cost-decrease'}>
                          {percentage(service.change_percent)}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          </div>

          <section className="cost-panel cost-reconciliation">
            <div className="cost-panel-heading">
              <div>
                <h2>Inventory-to-billing reconciliation</h2>
                <p>Compare resource inventory costs with reported cloud billing</p>
              </div>
              <span className="cost-api-label">CROSS-API ANALYSIS</span>
            </div>

            <div className="reconciliation-grid">
              <div className="reconciliation-item">
                <span>Reported billing</span>
                <strong>{money(billingCost, currency)}</strong>
                <small>Cost summary API</small>
              </div>
              <div className="reconciliation-item">
                <span>Inventoried resources</span>
                <strong>{money(inventoryCost, currency)}</strong>
                <small>Sum of asset monthly costs</small>
              </div>
              <div className="reconciliation-item reconciliation-gap">
                <span>Unmatched billing amount</span>
                <strong>{money(billingDifference, currency)}</strong>
                <small>{reconciliationPercent.toFixed(1)}% of reported billing</small>
              </div>
            </div>

            <div className="reconciliation-note">
              <Info size={17} />
              <p>
                {billingDifference > 0
                  ? `The billing API reports ${money(billingDifference, currency)} more than the sum of inventoried resources. This may represent shared services, untracked resources or different billing scopes. It has not been attributed to specific resources.`
                  : billingDifference < 0
                    ? `The inventory total exceeds reported billing by ${money(Math.abs(billingDifference), currency)}. Verify that both APIs use the same billing period and cost scope.`
                    : 'The inventory and billing totals currently match.'}
              </p>
            </div>
          </section>

          <div className="cost-bottom-grid">
            <section className="cost-panel">
              <div className="cost-panel-heading">
                <div>
                  <h2>
                    <AlertTriangle size={16} />
                    Cost anomalies
                  </h2>
                  <p>Findings returned by the cost anomaly API</p>
                </div>
                <span className="cost-count">{costAnomalies.length}</span>
              </div>

              {costAnomalies.length === 0 ? (
                <div className="cost-empty">
                  <Activity size={22} />
                  <strong>No anomalies returned</strong>
                  <span>The API did not report any cost anomalies.</span>
                </div>
              ) : (
                <div className="cost-anomaly-list">
                  {costAnomalies.map((anomaly, index) => (
                    <div className="cost-anomaly-item" key={`${anomaly.service}-${index}`}>
                      <div className="cost-anomaly-top">
                        <strong>{anomaly.service}</strong>
                        <span className={`anomaly-severity ${anomaly.severity}`}>
                          {anomaly.severity}
                        </span>
                      </div>
                      <div className="cost-anomaly-numbers">
                        <span>{money(anomaly.current_month, currency)}</span>
                        <span className="cost-increase">
                          <ArrowUpRight size={13} />
                          {percentage(anomaly.change_percent)}
                        </span>
                      </div>
                      <p>{anomaly.explanation}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="cost-panel">
              <div className="cost-panel-heading">
                <div>
                  <h2>
                    <Lightbulb size={16} />
                    Optimization opportunities
                  </h2>
                  <p>Based on inventoried CPU and memory utilization</p>
                </div>
              </div>

              {optimizationCandidates.length === 0 ? (
                <div className="cost-empty">
                  <Gauge size={22} />
                  <strong>No low-utilization candidates</strong>
                  <span>No resources currently meet the low CPU and memory thresholds.</span>
                </div>
              ) : (
                <>
                  <div className="optimization-summary">
                    <span>Monthly cost of identified candidates</span>
                    <strong>{money(potentialSavings, currency)}</strong>
                    <small>This is candidate spend, not guaranteed savings.</small>
                  </div>

                  <div className="optimization-list">
                    {optimizationCandidates.map(asset => (
                      <div className="optimization-item" key={asset.id}>
                        <div>
                          <strong>{asset.name}</strong>
                          <span>{asset.provider} · {asset.environment}</span>
                        </div>
                        <div>
                          <strong>{money(asset.monthly_cost, currency)}</strong>
                          <span>CPU {asset.cpu_utilization_percent.toFixed(1)}% · Memory {asset.memory_utilization_percent.toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </section>
          </div>

          <div className="cost-disclaimer">
            <Info size={14} />
            <span>
              Optimization candidates are heuristic signals for human review.
              They are not confirmed savings estimates or automatic infrastructure changes.
            </span>
          </div>
        </>
      )}
    </section>
  )
}

function CostMetric({
  label,
  value,
  caption,
  icon,
  tone,
}: {
  label: string
  value: string
  caption: string
  icon: React.ReactNode
  tone?: 'warning' | 'positive'
}) {
  return (
    <div className="cost-metric-card">
      <div className="cost-metric-top">
        <span>{label}</span>
        <div className="cost-metric-icon">{icon}</div>
      </div>
      <strong className={tone ? `cost-metric-value ${tone}` : 'cost-metric-value'}>
        {value}
      </strong>
      <span className="cost-metric-caption">{caption}</span>
    </div>
  )
}
