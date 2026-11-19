
import { useMemo, useState } from 'react'
import {
 AlertTriangle, CheckCircle2, Cpu, Gauge,
  MemoryStick, Search, Server, RefreshCw, Lightbulb,
  Cloud, Info,
} from 'lucide-react'
import type { Asset, UtilizationReport } from '../services/api'
import './Utilization.css'

interface UtilizationProps {
  utilization: UtilizationReport | null
  assets: Asset[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

type ProviderFilter = 'all' | 'AWS' | 'GCP'
type EnvironmentFilter = 'all' | 'production' | 'staging' | 'development'
type ClassificationFilter =
  | 'all'
  | 'underutilized'
  | 'healthy'
  | 'overutilized'

function average(values: number[]) {
  if (!values.length) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function percentage(value: number) {
  return `${value.toFixed(1)}%`
}

export function Utilization({
  utilization,
  assets,
  loading,
  error,
  onRefresh,
}: UtilizationProps) {
  const [search, setSearch] = useState('')
  const [provider, setProvider] = useState<ProviderFilter>('all')
  const [environment, setEnvironment] =
    useState<EnvironmentFilter>('all')
  const [classification, setClassification] =
    useState<ClassificationFilter>('all')

  const assetById = useMemo(
    () => new Map(assets.map(asset => [asset.id, asset])),
    [assets],
  )

  const items = utilization?.items ?? []

  const filteredItems = useMemo(() => {
    const query = search.trim().toLowerCase()

    return items.filter(item => {
      const asset = assetById.get(item.asset_id)

      const matchesSearch =
        !query ||
        item.asset_name.toLowerCase().includes(query) ||
        item.asset_id.toLowerCase().includes(query) ||
        item.resource_type.toLowerCase().includes(query) ||
        (asset?.owner_team ?? '').toLowerCase().includes(query)

      const matchesProvider =
        provider === 'all' || asset?.provider === provider

      const matchesEnvironment =
        environment === 'all' || asset?.environment === environment

      const matchesClassification =
        classification === 'all' ||
        item.classification === classification

      return (
        matchesSearch &&
        matchesProvider &&
        matchesEnvironment &&
        matchesClassification
      )
    })
  }, [items, assetById, search, provider, environment, classification])

  const avgCpu = average(items.map(item => item.cpu_utilization_percent))
  const avgMemory = average(items.map(item => item.memory_utilization_percent))

  const clearFilters = () => {
    setSearch('')
    setProvider('all')
    setEnvironment('all')
    setClassification('all')
  }

  const hasFilters =
    search !== '' ||
    provider !== 'all' ||
    environment !== 'all' ||
    classification !== 'all'

  return (
    <section className="utilization-page">
      <div className="utilization-heading">
        <div>
          <div className="eyebrow">
            CLOUD OPERATIONS / RESOURCE PERFORMANCE
          </div>
          <h1>Utilization intelligence</h1>
          <p>
            Monitor resource performance, identify capacity risks and
            discover rightsizing opportunities.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw
            size={15}
            className={loading ? 'utilization-spin' : ''}
          />
          Refresh analysis
        </button>
      </div>

      <div className="utilization-notice">
        <Info size={16} />
        <span>
          Utilization metrics are supplied by the backend demo dataset.
          Recommendations are advisory and do not change cloud resources.
        </span>
      </div>

      {error && (
        <div className="utilization-error">
          <AlertTriangle size={17} />
          <span>{error}</span>
          <button onClick={onRefresh}>Retry</button>
        </div>
      )}

      {!utilization && loading ? (
        <div className="utilization-empty">
          <RefreshCw size={20} className="utilization-spin" />
          Loading utilization analysis...
        </div>
      ) : !utilization ? (
        <div className="utilization-empty">
          <Gauge size={25} />
          <strong>Utilization data unavailable</strong>
          <span>Check the backend connection and refresh the analysis.</span>
        </div>
      ) : (
        <>
          <div className="utilization-metrics">
            <UtilMetric
              label="Total analyzed resources"
              value={String(utilization.total_assets)}
              caption="Resources in utilization report"
              icon={<Server size={19} />}
              tone="purple"
            />
            <UtilMetric
              label="Average CPU utilization"
              value={percentage(avgCpu)}
              caption="Across analyzed resources"
              icon={<Cpu size={19} />}
              tone="blue"
            />
            <UtilMetric
              label="Average memory utilization"
              value={percentage(avgMemory)}
              caption="Across analyzed resources"
              icon={<MemoryStick size={19} />}
              tone="green"
            />
            <UtilMetric
              label="Underutilized resources"
              value={String(utilization.underutilized)}
              caption="Potential optimization candidates"
              icon={<AlertTriangle size={19} />}
              tone="amber"
            />
          </div>

          <div className="utilization-classification-grid">
            <ClassificationCard
              label="Underutilized"
              count={utilization.underutilized}
              total={utilization.total_assets}
              description="Review for possible rightsizing"
              type="underutilized"
            />
            <ClassificationCard
              label="Healthy"
              count={utilization.healthy}
              total={utilization.total_assets}
              description="Within expected utilization range"
              type="healthy"
            />
            <ClassificationCard
              label="Overutilized"
              count={utilization.overutilized}
              total={utilization.total_assets}
              description="Review capacity and performance"
              type="overutilized"
            />
          </div>

          <section className="utilization-panel">
            <div className="utilization-panel-heading">
              <div>
                <h2>Resource utilization</h2>
                <p>CPU, memory and recommendations by resource</p>
              </div>
              <span className="utilization-api-label">API DATA</span>
            </div>

            <div className="utilization-filters">
              <div className="utilization-search">
                <Search size={16} />
                <input
                  value={search}
                  onChange={event => setSearch(event.target.value)}
                  placeholder="Search resource, ID, type or owner..."
                />
              </div>

              <label className="utilization-filter">
                <span>Provider</span>
                <select
                  value={provider}
                  onChange={event =>
                    setProvider(event.target.value as ProviderFilter)
                  }
                >
                  <option value="all">All providers</option>
                  <option value="AWS">AWS</option>
                  <option value="GCP">GCP</option>
                </select>
              </label>

              <label className="utilization-filter">
                <span>Environment</span>
                <select
                  value={environment}
                  onChange={event =>
                    setEnvironment(event.target.value as EnvironmentFilter)
                  }
                >
                  <option value="all">All environments</option>
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </label>

              <label className="utilization-filter">
                <span>Classification</span>
                <select
                  value={classification}
                  onChange={event =>
                    setClassification(
                      event.target.value as ClassificationFilter,
                    )
                  }
                >
                  <option value="all">All classifications</option>
                  <option value="underutilized">Underutilized</option>
                  <option value="healthy">Healthy</option>
                  <option value="overutilized">Overutilized</option>
                </select>
              </label>

              {hasFilters && (
                <button
                  className="utilization-clear"
                  onClick={clearFilters}
                >
                  Clear filters
                </button>
              )}
            </div>

            <div className="utilization-results">
              Showing <strong>{filteredItems.length}</strong> of{' '}
              <strong>{items.length}</strong> analyzed resources
            </div>

            {filteredItems.length === 0 ? (
              <div className="utilization-empty">
                <Search size={22} />
                <strong>No matching resources</strong>
                <span>Try changing your search or filters.</span>
              </div>
            ) : (
              <div className="utilization-table-wrap">
                <table className="utilization-table">
                  <thead>
                    <tr>
                      <th>Resource</th>
                      <th>Provider</th>
                      <th>Environment</th>
                      <th>CPU</th>
                      <th>Memory</th>
                      <th>Classification</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredItems.map(item => {
                      const asset = assetById.get(item.asset_id)

                      return (
                        <tr key={item.asset_id}>
                          <td>
                            <div className="util-resource">
                              <div className="util-resource-icon">
                                <Cloud size={17} />
                              </div>
                              <div>
                                <strong>{item.asset_name}</strong>
                                <span>{item.asset_id}</span>
                                {asset?.owner_team && (
                                  <small>{asset.owner_team}</small>
                                )}
                              </div>
                            </div>
                          </td>

                          <td>
                            {asset ? (
                              <span className={`util-provider ${asset.provider.toLowerCase()}`}>
                                {asset.provider}
                              </span>
                            ) : '—'}
                          </td>

                          <td>
                            {asset ? (
                              <span className={`util-environment ${asset.environment}`}>
                                {asset.environment}
                              </span>
                            ) : '—'}
                          </td>

                          <td>
                            <UtilBar value={item.cpu_utilization_percent} />
                          </td>

                          <td>
                            <UtilBar value={item.memory_utilization_percent} />
                          </td>

                          <td>
                            <ClassificationBadge
                              classification={item.classification}
                            />
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="utilization-panel utilization-recommendations">
            <div className="utilization-panel-heading">
              <div>
                <h2>
                  <Lightbulb size={17} />
                  Resource recommendations
                </h2>
                <p>Recommendations returned by the utilization analysis API</p>
              </div>
              <span className="utilization-api-label">BACKEND ANALYSIS</span>
            </div>

            <div className="util-recommendation-list">
              {filteredItems.length === 0 ? (
                <div className="utilization-empty">
                  No recommendations to display for these filters.
                </div>
              ) : (
                filteredItems.map(item => (
                  <div
                    className="util-recommendation"
                    key={item.asset_id}
                  >
                    <div className={`util-recommendation-icon ${item.classification}`}>
                      {item.classification === 'overutilized'
                        ? <AlertTriangle size={18} />
                        : item.classification === 'healthy'
                          ? <CheckCircle2 size={18} />
                          : <Lightbulb size={18} />}
                    </div>
                    <div className="util-recommendation-copy">
                      <strong>{item.asset_name}</strong>
                      <p>{item.recommendation}</p>
                    </div>
                    <ClassificationBadge
                      classification={item.classification}
                    />
                  </div>
                ))
              )}
            </div>
          </section>

          <div className="utilization-disclaimer">
            <Info size={14} />
            <span>
              Utilization classifications and recommendations are based on
              backend analysis. Review workload patterns, service-level
              requirements and business criticality before changing capacity.
            </span>
          </div>
        </>
      )}
    </section>
  )
}

function UtilMetric({
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
  tone: 'purple' | 'blue' | 'green' | 'amber'
}) {
  return (
    <div className="util-metric-card">
      <div className="util-metric-top">
        <span>{label}</span>
        <div className={`util-metric-icon ${tone}`}>{icon}</div>
      </div>
      <strong>{value}</strong>
      <small>{caption}</small>
    </div>
  )
}

function ClassificationCard({
  label,
  count,
  total,
  description,
  type,
}: {
  label: string
  count: number
  total: number
  description: string
  type: 'underutilized' | 'healthy' | 'overutilized'
}) {
  const share = total > 0 ? (count / total) * 100 : 0

  return (
    <div className={`util-classification-card ${type}`}>
      <div className="util-classification-top">
        <span>{label}</span>
        <strong>{count}</strong>
      </div>
      <div className="util-classification-track">
        <div style={{ width: `${share}%` }} />
      </div>
      <small>{description}</small>
    </div>
  )
}

function UtilBar({ value }: { value: number }) {
  const safeValue = Math.max(0, Math.min(100, value))
  const tone =
    safeValue >= 85 ? 'high' : safeValue < 20 ? 'low' : 'normal'

  return (
    <div className="util-bar-cell">
      <strong>{percentage(value)}</strong>
      <div className="util-bar-track">
        <div
          className={`util-bar-fill ${tone}`}
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  )
}

function ClassificationBadge({
  classification,
}: {
  classification: 'underutilized' | 'healthy' | 'overutilized'
}) {
  return (
    <span className={`util-classification-badge ${classification}`}>
      <span />
      {classification}
    </span>
  )
}
