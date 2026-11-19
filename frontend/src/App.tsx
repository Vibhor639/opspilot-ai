
import { useState } from 'react'
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight,
  Bell, Bot, CheckCircle2, ChevronDown, CircleDollarSign,
  Cloud, Command, Cpu, Database, Gauge, LayoutDashboard,
  LifeBuoy, LoaderCircle, Menu, Network, RefreshCw, Search,
  Settings, ShieldCheck, Sparkles, X, Zap,
} from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer,
  Tooltip, XAxis, YAxis, PieChart, Pie, Cell,
} from 'recharts'
import { useDashboardData } from './hooks/useDashboardData'
import type { Asset, Incident } from './services/api'
import './App.css'
import { CloudInventory } from './components/CloudInventory'
import { CostIntelligence } from './components/CostIntelligence'
import { Utilization } from './components/Utilization'
import { Incidents } from './components/Incidents'
import { AIInvestigations } from './components/AIInvestigations'

const navigation = [
  { label: 'Overview', icon: LayoutDashboard, group: 'WORKSPACE' },
  { label: 'Cloud inventory', icon: Cloud, group: 'WORKSPACE' },
  { label: 'Cost intelligence', icon: CircleDollarSign, group: 'WORKSPACE' },
  { label: 'Utilization', icon: Gauge, group: 'WORKSPACE' },
  { label: 'Incidents', icon: AlertTriangle, group: 'OPERATIONS' },
  { label: 'AI investigations', icon: Bot, group: 'OPERATIONS' },
  { label: 'Approvals', icon: ShieldCheck, group: 'OPERATIONS' },
  { label: 'Knowledge base', icon: Database, group: 'PLATFORM' },
  { label: 'MCP integrations', icon: Network, group: 'PLATFORM' },
]

const pageDescriptions: Record<string, string> = {
  'Cloud inventory': 'Explore your cloud resources across providers.',
  'Cost intelligence': 'Understand cloud spending and identify cost anomalies.',
  'Utilization': 'Monitor resource utilization and optimization opportunities.',
  'Incidents': 'Track operational incidents across your cloud environment.',
  'AI investigations': 'Investigate operational issues with your AI agent team.',
  'Approvals': 'Review and manage human approval requests for remediation.',
  'Knowledge base': 'Search runbooks, documents and operational knowledge.',
  'MCP integrations': 'Inspect connected tools and cloud integration status.',
  Settings: 'Manage your OpsPilot AI workspace preferences.',
}

const providerColors: Record<string, string> = {
  AWS: '#9b8cff',
  GCP: '#43c6ac',
}

function formatCurrency(value: number, currency: string) {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0,
    }).format(value)
  } catch {
    return `${currency || ''} ${value.toLocaleString()}`
  }
}

function averageCpu(assets: Asset[]) {
  if (!assets.length) return 0
  return assets.reduce((total, asset) => total + asset.cpu_utilization_percent, 0) / assets.length
}

function App() {
  const [activePage, setActivePage] = useState('Overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [search, setSearch] = useState('')

  const {
    assets,
    costSummary,
    costAnomalies,
    incidents,
    utilization,
    cloudStatus,
    loading,
    error,
    lastUpdated,
    refresh,
  } = useDashboardData()

  const isOverview = activePage === 'Overview'
  const currency = costSummary?.currency || 'USD'

  const openIncidents = incidents.filter(
    incident => incident.status !== 'resolved',
  ).length

  const providerCounts = [
    { name: 'AWS', value: assets.filter(asset => asset.provider === 'AWS').length, color: providerColors.AWS },
    { name: 'GCP', value: assets.filter(asset => asset.provider === 'GCP').length, color: providerColors.GCP },
  ].filter(item => item.value > 0)

  const costChartData = (costSummary?.services || []).map(service => ({
    month: service.service,
    cost: service.current_month,
  }))

  const cpu = averageCpu(assets)

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="mobile-backdrop"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close menu"
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-icon"><Command size={21} /></div>
          <div>
            <div className="brand-name">OpsPilot<span> AI</span></div>
            <div className="brand-subtitle">CLOUD OPERATIONS</div>
          </div>
          <button className="mobile-close" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar">
            <X size={19} />
          </button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-avatar">O</div>
          <div className="workspace-copy">
            <strong>Operations workspace</strong>
            <span>Personal environment</span>
          </div>
          <ChevronDown size={15} className="muted-icon" />
        </div>

        <nav className="side-navigation">
          {['WORKSPACE', 'OPERATIONS', 'PLATFORM'].map(group => (
            <div className="nav-group" key={group}>
              <div className="nav-heading">{group}</div>
              {navigation.filter(item => item.group === group).map(item => {
                const Icon = item.icon
                return (
                  <button
                    key={item.label}
                    className={`nav-link ${activePage === item.label ? 'active' : ''}`}
                    onClick={() => {
                      setActivePage(item.label)
                      setSidebarOpen(false)
                    }}
                  >
                    <Icon size={17} strokeWidth={1.8} />
                    <span>{item.label}</span>
                    {item.label === 'Incidents' && openIncidents > 0 && (
                      <span className="nav-count">{openIncidents}</span>
                    )}
                  </button>
                )
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon"><LifeBuoy size={17} /></div>
            <div>
              <strong>Need assistance?</strong>
              <span>Explore the documentation</span>
            </div>
          </div>
          <button className="nav-link settings-link" onClick={() => setActivePage('Settings')}>
            <Settings size={17} /><span>Settings</span>
          </button>
          <div className="profile">
            <div className="profile-avatar">VT</div>
            <div className="profile-copy">
              <strong>Workspace admin</strong>
              <span>Administrator</span>
            </div>
            <ChevronDown size={15} className="muted-icon" />
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
              <Menu size={21} />
            </button>
            <div className="breadcrumb">
              Workspace <span>/</span> <strong>{activePage}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <label className="search-box">
              <Search size={16} />
              <input
                value={search}
                onChange={event => setSearch(event.target.value)}
                placeholder="Search anything..."
              />
              <kbd>⌘ K</kbd>
            </label>
            <div className="environment-pill"><span /> Demo environment</div>
            <button className="icon-button" aria-label="Notifications">
              <Bell size={18} />
            </button>
            <div className="topbar-avatar">VT</div>
          </div>
        </header>

        <div className="page-content">
          {isOverview ? (
            <>
              <section className="page-heading">
                <div>
                  <div className="eyebrow"><Sparkles size={13} /> OPERATIONS CENTER</div>
                  <h1>Good afternoon, Vibhor <span className="wave">✦</span></h1>
                  <p>Here's what's happening across your cloud infrastructure.</p>
                </div>

                <div className="heading-actions">
                  <button className="secondary-button" onClick={() => void refresh()} disabled={loading}>
                    {loading
                      ? <LoaderCircle size={14} className="spin" />
                      : <RefreshCw size={14} />}
                    Refresh
                  </button>
                  <button className="primary-button" onClick={() => setActivePage('AI investigations')}>
                    <Sparkles size={16} /> New investigation
                  </button>
                </div>
              </section>

              <div className="demo-notice">
                <Activity size={15} />
                <span>
                  <strong>Demo cloud mode:</strong> These values come from your FastAPI backend's demo dataset, not live AWS/GCP accounts.
                </span>
              </div>

              {error && (
                <div className="api-error">
                  <AlertTriangle size={17} />
                  <div>
                    <strong>Some dashboard data could not be loaded</strong>
                    <p>{error}</p>
                  </div>
                  <button onClick={() => void refresh()}>Retry</button>
                </div>
              )}

              {loading && !lastUpdated ? (
                <div className="dashboard-loading">
                  <LoaderCircle size={25} className="spin" />
                  <span>Loading cloud operations data...</span>
                </div>
              ) : (
                <>
                  <section className="metric-grid">
                    <MetricCard
                      title="Total cloud spend"
                      value={costSummary ? formatCurrency(costSummary.current_month, currency) : '—'}
                      change={costSummary ? `${costSummary.change_percent.toFixed(1)}%` : 'Unavailable'}
                      positive={costSummary ? costSummary.change_percent <= 0 : true}
                      icon={<CircleDollarSign size={18} />}
                      caption="vs. previous month"
                    />
                    <MetricCard
                      title="Cloud resources"
                      value={assets.length.toLocaleString()}
                      change="Inventory"
                      positive
                      icon={<Cloud size={18} />}
                      caption="AWS and GCP assets"
                    />
                    <MetricCard
                      title="Open incidents"
                      value={openIncidents.toString()}
                      change={`${incidents.length} total`}
                      positive={openIncidents === 0}
                      icon={<AlertTriangle size={18} />}
                      caption="Not yet resolved"
                    />
                    <MetricCard
                      title="Avg. CPU utilization"
                      value={assets.length ? `${cpu.toFixed(1)}%` : '—'}
                      change="Current"
                      positive={cpu <= 80}
                      icon={<Cpu size={18} />}
                      caption="Across inventoried assets"
                    />
                  </section>

                  <section className="dashboard-grid">
                    <div className="panel cost-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>Cloud expenditure</h2>
                          <p>Current month spend by service</p>
                        </div>
                        <span className="data-source-label">API DATA</span>
                      </div>

                      <div className="chart-summary">
                        <div>
                          <strong>
                            {costSummary
                              ? formatCurrency(costSummary.current_month, currency)
                              : 'No data'}
                          </strong>
                          {costSummary && (
                            <span className={costSummary.change_percent <= 0 ? 'trend-good' : 'trend-bad'}>
                              {costSummary.change_percent > 0
                                ? <ArrowUpRight size={14} />
                                : <ArrowDownRight size={14} />}
                              {Math.abs(costSummary.change_percent).toFixed(1)}%
                              <small>vs last month</small>
                            </span>
                          )}
                        </div>
                        <div className="chart-legend"><i /> Current month</div>
                      </div>

                      <div className="cost-chart">
                        {costChartData.length ? (
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={costChartData} margin={{ top: 10, right: 8, left: -12, bottom: 0 }}>
                              <defs>
                                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="0%" stopColor="#9b8cff" stopOpacity={0.28} />
                                  <stop offset="100%" stopColor="#9b8cff" stopOpacity={0} />
                                </linearGradient>
                              </defs>
                              <CartesianGrid stroke="#242b3b" strokeDasharray="3 5" vertical={false} />
                              <XAxis dataKey="month" tick={{ fill: '#7f8ba1', fontSize: 10 }} axisLine={false} tickLine={false} />
                              <YAxis
                                tick={{ fill: '#7f8ba1', fontSize: 10 }}
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={value => formatCurrency(Number(value), currency)}
                              />
                              <Tooltip
                                contentStyle={{ background: '#171e2d', border: '1px solid #30394d', borderRadius: 9, color: '#fff' }}
                                formatter={value => [formatCurrency(Number(value), currency), 'Spend']}
                              />
                              <Area type="monotone" dataKey="cost" stroke="#a394ff" strokeWidth={2.5} fill="url(#costGradient)" />
                            </AreaChart>
                          </ResponsiveContainer>
                        ) : (
                          <EmptyState message="No service-level cost data returned by the API." />
                        )}
                      </div>
                    </div>

                    <div className="panel distribution-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>Cloud distribution</h2>
                          <p>Resources by provider</p>
                        </div>
                        <span className="data-source-label">API DATA</span>
                      </div>

                      <div className="donut-wrap">
                        {providerCounts.length ? (
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={providerCounts}
                                dataKey="value"
                                nameKey="name"
                                innerRadius={66}
                                outerRadius={88}
                                paddingAngle={5}
                                stroke="none"
                              >
                                {providerCounts.map(entry => (
                                  <Cell key={entry.name} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip
                                contentStyle={{ background: '#171e2d', border: '1px solid #30394d', borderRadius: 9, color: '#fff' }}
                                formatter={value => [Number(value), 'Resources']}
                              />
                            </PieChart>
                          </ResponsiveContainer>
                        ) : (
                          <EmptyState message="No cloud assets found." />
                        )}

                        <div className="donut-center">
                          <strong>{assets.length.toLocaleString()}</strong>
                          <span>Total assets</span>
                        </div>
                      </div>

                      <div className="provider-legend">
                        {providerCounts.map(item => (
                          <div key={item.name}>
                            <span><i style={{ background: item.color }} />{item.name}</span>
                            <strong>
                              {assets.length
                                ? `${((item.value / assets.length) * 100).toFixed(1)}%`
                                : '0%'}
                            </strong>
                          </div>
                        ))}
                      </div>
                    </div>
                  </section>

                  <section className="lower-grid">
                    <div className="panel incidents-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>Recent incidents</h2>
                          <p>Latest incidents returned by your backend</p>
                        </div>
                        <button className="text-button" onClick={() => setActivePage('Incidents')}>
                          View all <ArrowUpRight size={14} />
                        </button>
                      </div>

                      <div className="incident-list">
                        {incidents.length ? incidents.slice(0, 5).map(incident => (
                          <IncidentRow key={incident.id} incident={incident} />
                        )) : (
                          <EmptyState message="No incidents returned by the API." />
                        )}
                      </div>
                    </div>

                    <div className="panel health-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>Platform health</h2>
                          <p>Backend integration overview</p>
                        </div>
                        <span className="health-indicator"><i /> Connected</span>
                      </div>

                      <div className="health-list">
                        <HealthRow icon={<Cloud size={17} />} name="AWS / GCP inventory" status={assets.length ? 'Available' : 'No assets'} />
                        <HealthRow icon={<CircleDollarSign size={17} />} name="Cost intelligence" status={costSummary ? 'Available' : 'Unavailable'} />
                        <HealthRow icon={<Bot size={17} />} name="AI agent engine" status="API available" />
                        <HealthRow icon={<Network size={17} />} name="Cloud status endpoint" status={cloudStatus ? 'Responding' : 'Unavailable'} />
                      </div>

                      <button className="integration-link" onClick={() => setActivePage('MCP integrations')}>
                        View integrations <ArrowUpRight size={14} />
                      </button>
                    </div>
                  </section>

                  <div className="dashboard-extra">
                    <div>
                      <strong>Cost anomalies detected</strong>
                      <span>{costAnomalies.length} returned by the cost intelligence API</span>
                    </div>
                    <div>
                      <strong>Utilization analysis</strong>
                      <span>
                        {utilization
                          ? `${utilization.underutilized} underutilized · ${utilization.healthy} healthy · ${utilization.overutilized} overutilized`
                          : 'Unavailable'}
                      </span>
                    </div>
                  </div>
                </>
              )}

              <footer className="page-footer">
                <span>OpsPilot AI <i>·</i> Cloud operations intelligence</span>
                <span>
                  {lastUpdated
                    ? `Last updated ${lastUpdated.toLocaleTimeString()}`
                    : 'Waiting for API data'}
                </span>
              </footer>
            </>
                              ) : activePage === 'Cloud inventory' ? (
            <CloudInventory
              assets={assets}
              loading={loading}
              error={error}
              onRefresh={refresh}
            />
                    ) : activePage === 'Cost intelligence' ? (
            <CostIntelligence
              costSummary={costSummary}
              costAnomalies={costAnomalies}
              assets={assets}
              loading={loading}
              error={error}
              onRefresh={refresh}
            />
                    ) : activePage === 'Utilization' ? (
            <Utilization
              utilization={utilization}
              assets={assets}
              loading={loading}
              error={error}
              onRefresh={refresh}
            />
          ) : activePage === 'Incidents' ? (
  <Incidents
    incidents={incidents}
    assets={assets}
    loading={loading}
    error={error}
    onRefresh={refresh}
  />
) : activePage === 'AI investigations' ? (
  <AIInvestigations />
) : (
  <section className="placeholder-page">
              <div className="placeholder-icon"><Zap size={25} /></div>
              <div className="eyebrow">OPSPILOT AI WORKSPACE</div>
              <h1>{activePage}</h1>
              <p>{pageDescriptions[activePage] ?? 'Manage your OpsPilot AI workspace preferences.'}</p>
              <div className="placeholder-card">
                <div className="placeholder-card-icon"><Activity size={20} /></div>
                <div>
                  <strong>{activePage} module</strong>
                  <span>This section will be connected to its corresponding backend workflows in the next implementation steps.</span>
                </div>
                <span className="coming-soon">IN PROGRESS</span>
              </div>
              <button className="secondary-button back-button" onClick={() => setActivePage('Overview')}>
                Back to overview
              </button>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

function MetricCard({ title, value, change, positive, icon, caption }: {
  title: string
  value: string
  change: string
  positive: boolean
  icon: React.ReactNode
  caption: string
}) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{title}</span>
        <div className="metric-icon">{icon}</div>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-bottom">
        <span className={`metric-change ${positive ? 'good' : 'bad'}`}>
          {positive ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}
          {change}
        </span>
        <span>{caption}</span>
      </div>
    </div>
  )
}

function IncidentRow({ incident }: { incident: Incident }) {
  const severity = incident.severity.toLowerCase()
  const status = incident.status.toLowerCase()

  return (
    <div className="incident-row">
      <div className={`severity-indicator ${severity}`} />
      <div className="incident-main">
        <strong>{incident.title}</strong>
        <span>
          {incident.id} <i>·</i> {incident.affected_asset_ids.length} affected asset(s)
        </span>
      </div>
      <span className={`severity-badge ${severity}`}>{incident.severity}</span>
      <span className={`status-text ${status}`}>{incident.status}</span>
    </div>
  )
}

function HealthRow({ icon, name, status }: {
  icon: React.ReactNode
  name: string
  status: string
}) {
  const ready = status === 'Available' || status === 'Responding' || status === 'API available'

  return (
    <div className="health-row">
      <div className="health-row-icon">{icon}</div>
      <strong>{name}</strong>
      <span className={`health-status ${ready ? 'ready' : ''}`}>
        {ready && <CheckCircle2 size={13} />}
        {status}
      </span>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return <div className="empty-state">{message}</div>
}

export default App
