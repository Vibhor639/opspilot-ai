
import { useMemo, useState } from 'react'
import {
  Search, RefreshCw, Cloud, Server, Database, HardDrive,
  Cpu, MemoryStick, DollarSign, MapPin, Users, Tag,
  X, ChevronDown, ArrowUpDown, ExternalLink,
} from 'lucide-react'
import type { Asset } from '../services/api'
import './CloudInventory.css'

type ProviderFilter = 'All' | 'AWS' | 'GCP'
type EnvironmentFilter = 'All' | Asset['environment']
type SortField = 'name' | 'monthly_cost' | 'cpu_utilization_percent' | 'memory_utilization_percent'

interface CloudInventoryProps {
  assets: Asset[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

function getResourceIcon(resourceType: string) {
  const type = resourceType.toLowerCase()

  if (type.includes('database') || type.includes('sql') || type.includes('rds')) {
    return Database
  }

  if (type.includes('storage') || type.includes('disk') || type.includes('bucket')) {
    return HardDrive
  }

  if (type.includes('server') || type.includes('instance') || type.includes('compute') || type.includes('vm')) {
    return Server
  }

  return Cloud
}

function getHealth(asset: Asset) {
  if (
    asset.cpu_utilization_percent >= 80 ||
    asset.memory_utilization_percent >= 85
  ) {
    return { label: 'High utilization', className: 'high' }
  }

  if (
    asset.cpu_utilization_percent < 20 &&
    asset.memory_utilization_percent < 30
  ) {
    return { label: 'Underutilized', className: 'low' }
  }

  return { label: 'Healthy', className: 'healthy' }
}

export function CloudInventory({
  assets,
  loading,
  error,
  onRefresh,
}: CloudInventoryProps) {
  const [search, setSearch] = useState('')
  const [provider, setProvider] = useState<ProviderFilter>('All')
  const [environment, setEnvironment] = useState<EnvironmentFilter>('All')
  const [resourceType, setResourceType] = useState('All')
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortDescending, setSortDescending] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)

  const resourceTypes = useMemo(
    () => [...new Set(assets.map(asset => asset.resource_type))].sort(),
    [assets],
  )

  const filteredAssets = useMemo(() => {
    const query = search.trim().toLowerCase()

    const result = assets.filter(asset => {
      const matchesSearch =
        !query ||
        asset.name.toLowerCase().includes(query) ||
        asset.id.toLowerCase().includes(query) ||
        asset.region.toLowerCase().includes(query) ||
        asset.owner_team.toLowerCase().includes(query)

      const matchesProvider =
        provider === 'All' || asset.provider === provider

      const matchesEnvironment =
        environment === 'All' || asset.environment === environment

      const matchesType =
        resourceType === 'All' || asset.resource_type === resourceType

      return matchesSearch && matchesProvider && matchesEnvironment && matchesType
    })

    return [...result].sort((a, b) => {
      const first = a[sortField]
      const second = b[sortField]

      const comparison =
        typeof first === 'string' && typeof second === 'string'
          ? first.localeCompare(second)
          : Number(first) - Number(second)

      return sortDescending ? -comparison : comparison
    })
  }, [assets, search, provider, environment, resourceType, sortField, sortDescending])

  const totalMonthlyCost = filteredAssets.reduce(
    (total, asset) => total + asset.monthly_cost,
    0,
  )

  const awsCount = filteredAssets.filter(asset => asset.provider === 'AWS').length
  const gcpCount = filteredAssets.filter(asset => asset.provider === 'GCP').length

  function changeSort(field: SortField) {
    if (sortField === field) {
      setSortDescending(current => !current)
    } else {
      setSortField(field)
      setSortDescending(false)
    }
  }

  function clearFilters() {
    setSearch('')
    setProvider('All')
    setEnvironment('All')
    setResourceType('All')
  }

  return (
    <section className="inventory-page">
      <div className="inventory-heading">
        <div>
          <div className="eyebrow">CLOUD OPERATIONS / RESOURCE MANAGEMENT</div>
          <h1>Cloud inventory</h1>
          <p>Discover, search and inspect your cloud infrastructure across providers.</p>
        </div>

        <button className="secondary-button" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={15} className={loading ? 'inventory-spin' : ''} />
          Refresh inventory
        </button>
      </div>

      <div className="inventory-summary">
        <div className="inventory-stat">
          <div className="inventory-stat-icon purple"><Cloud size={19} /></div>
          <div>
            <span>Total resources</span>
            <strong>{assets.length}</strong>
          </div>
        </div>

        <div className="inventory-stat">
          <div className="inventory-stat-icon orange"><Cloud size={19} /></div>
          <div>
            <span>AWS resources</span>
            <strong>{assets.filter(asset => asset.provider === 'AWS').length}</strong>
          </div>
        </div>

        <div className="inventory-stat">
          <div className="inventory-stat-icon blue"><Cloud size={19} /></div>
          <div>
            <span>GCP resources</span>
            <strong>{assets.filter(asset => asset.provider === 'GCP').length}</strong>
          </div>
        </div>

        <div className="inventory-stat">
          <div className="inventory-stat-icon green"><DollarSign size={19} /></div>
          <div>
            <span>Filtered monthly cost</span>
            <strong>{formatCurrency(totalMonthlyCost)}</strong>
          </div>
        </div>
      </div>

      <div className="inventory-toolbar">
        <div className="inventory-search">
          <Search size={16} />
          <input
            value={search}
            onChange={event => setSearch(event.target.value)}
            placeholder="Search name, ID, region or owner..."
            aria-label="Search cloud resources"
          />
          {search && (
            <button onClick={() => setSearch('')} aria-label="Clear search">
              <X size={14} />
            </button>
          )}
        </div>

        <label className="inventory-select">
          <span>Provider</span>
          <select value={provider} onChange={event => setProvider(event.target.value as ProviderFilter)}>
            <option value="All">All providers</option>
            <option value="AWS">AWS</option>
            <option value="GCP">GCP</option>
          </select>
          <ChevronDown size={13} />
        </label>

        <label className="inventory-select">
          <span>Environment</span>
          <select value={environment} onChange={event => setEnvironment(event.target.value as EnvironmentFilter)}>
            <option value="All">All environments</option>
            <option value="production">Production</option>
            <option value="staging">Staging</option>
            <option value="development">Development</option>
          </select>
          <ChevronDown size={13} />
        </label>

        <label className="inventory-select">
          <span>Resource type</span>
          <select value={resourceType} onChange={event => setResourceType(event.target.value)}>
            <option value="All">All types</option>
            {resourceTypes.map(type => (
              <option value={type} key={type}>{type}</option>
            ))}
          </select>
          <ChevronDown size={13} />
        </label>

        <button className="inventory-clear" onClick={clearFilters}>
          Clear filters
        </button>
      </div>

      <div className="inventory-results-bar">
        <span>
          Showing <strong>{filteredAssets.length}</strong> of <strong>{assets.length}</strong> resources
        </span>
        <span>
          AWS: <strong>{awsCount}</strong>
          <span className="inventory-dot">·</span>
          GCP: <strong>{gcpCount}</strong>
        </span>
      </div>

      {error && (
        <div className="inventory-error">
          {error}
          <button onClick={onRefresh}>Retry</button>
        </div>
      )}

      <div className="inventory-table-wrap">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>RESOURCE</th>
              <th>PROVIDER</th>
              <th>TYPE</th>
              <th>REGION</th>
              <th>ENVIRONMENT</th>
              <th>
                <button onClick={() => changeSort('monthly_cost')}>
                  MONTHLY COST <ArrowUpDown size={12} />
                </button>
              </th>
              <th>
                <button onClick={() => changeSort('cpu_utilization_percent')}>
                  CPU <ArrowUpDown size={12} />
                </button>
              </th>
              <th>HEALTH</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {loading && assets.length === 0 ? (
              <tr>
                <td colSpan={9} className="inventory-empty">
                  <RefreshCw size={19} className="inventory-spin" />
                  <span>Loading cloud resources...</span>
                </td>
              </tr>
            ) : filteredAssets.length === 0 ? (
              <tr>
                <td colSpan={9} className="inventory-empty">
                  <Cloud size={24} />
                  <strong>No resources found</strong>
                  <span>Try changing your search or filters.</span>
                  <button onClick={clearFilters}>Clear filters</button>
                </td>
              </tr>
            ) : (
              filteredAssets.map(asset => {
                const ResourceIcon = getResourceIcon(asset.resource_type)
                const health = getHealth(asset)

                return (
                  <tr key={asset.id} onClick={() => setSelectedAsset(asset)}>
                    <td>
                      <div className="inventory-resource">
                        <div className="inventory-resource-icon">
                          <ResourceIcon size={17} />
                        </div>
                        <div>
                          <strong>{asset.name}</strong>
                          <span>{asset.id}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`provider-badge ${asset.provider.toLowerCase()}`}>
                        {asset.provider}
                      </span>
                    </td>
                    <td>{asset.resource_type}</td>
                    <td>{asset.region}</td>
                    <td>
                      <span className={`environment-badge ${asset.environment}`}>
                        {asset.environment}
                      </span>
                    </td>
                    <td className="inventory-cost">{formatCurrency(asset.monthly_cost)}</td>
                    <td>{asset.cpu_utilization_percent.toFixed(1)}%</td>
                    <td>
                      <span className={`health-badge ${health.className}`}>
                        <span />
                        {health.label}
                      </span>
                    </td>
                    <td>
                      <button
                        className="inventory-open"
                        aria-label={`View ${asset.name}`}
                        onClick={event => {
                          event.stopPropagation()
                          setSelectedAsset(asset)
                        }}
                      >
                        <ExternalLink size={15} />
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="inventory-footnote">
        <span>Resource data provided by the OpsPilot API.</span>
        <span>Utilization health labels are heuristic classifications based on CPU and memory metrics.</span>
      </div>

      {selectedAsset && (
        <div className="asset-modal-backdrop" onClick={() => setSelectedAsset(null)}>
          <aside
            className="asset-detail-panel"
            onClick={event => event.stopPropagation()}
            aria-label="Cloud resource details"
          >
            <div className="asset-detail-header">
              <div>
                <div className="eyebrow">RESOURCE DETAILS</div>
                <h2>{selectedAsset.name}</h2>
                <span>{selectedAsset.id}</span>
              </div>
              <button className="icon-button" onClick={() => setSelectedAsset(null)} aria-label="Close details">
                <X size={18} />
              </button>
            </div>

            <div className="asset-detail-provider">
              <span className={`provider-badge ${selectedAsset.provider.toLowerCase()}`}>
                {selectedAsset.provider}
              </span>
              <span className={`environment-badge ${selectedAsset.environment}`}>
                {selectedAsset.environment}
              </span>
              <span className={`health-badge ${getHealth(selectedAsset).className}`}>
                <span />
                {getHealth(selectedAsset).label}
              </span>
            </div>

            <div className="asset-detail-section">
              <h3>Resource information</h3>
              <div className="asset-detail-grid">
                <DetailItem icon={<Server size={15} />} label="Resource type" value={selectedAsset.resource_type} />
                <DetailItem icon={<MapPin size={15} />} label="Region" value={selectedAsset.region} />
                <DetailItem icon={<Users size={15} />} label="Owner team" value={selectedAsset.owner_team} />
                <DetailItem icon={<DollarSign size={15} />} label="Monthly cost" value={formatCurrency(selectedAsset.monthly_cost)} />
                <DetailItem icon={<DollarSign size={15} />} label="Previous monthly cost" value={formatCurrency(selectedAsset.previous_monthly_cost)} />
              </div>
            </div>

            <div className="asset-detail-section">
              <h3>Resource utilization</h3>
              <UtilizationBar
                icon={<Cpu size={15} />}
                label="CPU utilization"
                value={selectedAsset.cpu_utilization_percent}
              />
              <UtilizationBar
                icon={<MemoryStick size={15} />}
                label="Memory utilization"
                value={selectedAsset.memory_utilization_percent}
              />
            </div>

            <div className="asset-detail-section">
              <h3><Tag size={15} /> Resource tags</h3>
              {Object.keys(selectedAsset.tags || {}).length === 0 ? (
                <span className="inventory-muted">No tags available.</span>
              ) : (
                <div className="asset-tags">
                  {Object.entries(selectedAsset.tags).map(([key, value]) => (
                    <div className="asset-tag" key={key}>
                      <span>{key}</span>
                      <strong>{value}</strong>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </aside>
        </div>
      )}
    </section>
  )
}

function DetailItem({ icon, label, value }: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="asset-detail-item">
      <div>{icon}<span>{label}</span></div>
      <strong>{value}</strong>
    </div>
  )
}

function UtilizationBar({ icon, label, value }: {
  icon: React.ReactNode
  label: string
  value: number
}) {
  const safeValue = Math.max(0, Math.min(100, value))

  return (
    <div className="utilization-bar-item">
      <div className="utilization-bar-label">
        <span>{icon}{label}</span>
        <strong>{value.toFixed(1)}%</strong>
      </div>
      <div className="utilization-track">
        <div className="utilization-fill" style={{ width: `${safeValue}%` }} />
      </div>
    </div>
  )
}
