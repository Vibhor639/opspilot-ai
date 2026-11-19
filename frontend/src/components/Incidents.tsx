
import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle, Activity, Bot, ChevronRight,
  Clock, Cloud, FileSearch, Lightbulb, RefreshCw, Search,
  ShieldAlert, Server, Info,
} from 'lucide-react'
import {
  apiService,
  getApiError,
} from '../services/api'
import type {
  Asset,
  Incident,
  InvestigationResult,
} from '../services/api'
import './Incidents.css'

interface IncidentsProps {
  incidents: Incident[]
  assets: Asset[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

type SeverityFilter = 'all' | 'critical' | 'high' | 'medium' | 'low'
type StatusFilter = 'all' | 'open' | 'investigating' | 'resolved'

const severityOrder: Record<Incident['severity'], number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
}

export function Incidents({
  incidents,
  assets,
  loading,
  error,
  onRefresh,
}: IncidentsProps) {
  const [search, setSearch] = useState('')
  const [severity, setSeverity] = useState<SeverityFilter>('all')
  const [status, setStatus] = useState<StatusFilter>('all')
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(
    incidents[0]?.id ?? null,
  )
  const [investigatingId, setInvestigatingId] = useState<string | null>(null)
  const [investigation, setInvestigation] =
    useState<InvestigationResult | null>(null)
  const [investigationError, setInvestigationError] = useState<string | null>(
    null,
  )
  useEffect(() => {
    if (!selectedIncidentId && incidents.length > 0) {
      setSelectedIncidentId(incidents[0].id)
    }
  }, [incidents, selectedIncidentId])
  const assetById = useMemo(
    () => new Map(assets.map(asset => [asset.id, asset])),
    [assets],
  )

  const filteredIncidents = useMemo(() => {
    const query = search.trim().toLowerCase()

    return incidents
      .filter(incident => {
        const affectedNames = incident.affected_asset_ids
          .map(id => assetById.get(id)?.name ?? '')
          .join(' ')

        const matchesSearch =
          !query ||
          incident.id.toLowerCase().includes(query) ||
          incident.title.toLowerCase().includes(query) ||
          affectedNames.toLowerCase().includes(query)

        return (
          matchesSearch &&
          (severity === 'all' || incident.severity === severity) &&
          (status === 'all' || incident.status === status)
        )
      })
      .sort(
        (a, b) => severityOrder[a.severity] - severityOrder[b.severity],
      )
  }, [incidents, assetById, search, severity, status])

  const selectedIncident =
    incidents.find(item => item.id === selectedIncidentId) ?? null

  const openCount = incidents.filter(item => item.status === 'open').length
  const investigatingCount = incidents.filter(
    item => item.status === 'investigating',
  ).length
  const criticalCount = incidents.filter(
    item => item.severity === 'critical',
  ).length

  const selectIncident = (incident: Incident) => {
    setSelectedIncidentId(incident.id)
    setInvestigation(null)
    setInvestigationError(null)
  }

  const runInvestigation = async (incident: Incident) => {
    const affectedResources = incident.affected_asset_ids.map(id => {
      const asset = assetById.get(id)
      return asset
        ? `${asset.name} (${asset.provider}, ${asset.resource_type}, ${asset.region})`
        : id
    })

    const question = [
      `Investigate incident ${incident.id}: ${incident.title}.`,
      `Severity: ${incident.severity}.`,
      `Current status: ${incident.status}.`,
      `Affected resources: ${affectedResources.join(', ') || 'Not specified'}.`,
      'Analyze likely causes, relevant evidence, operational impact and safe recommended next steps.',
      'Do not execute any infrastructure changes.',
    ].join(' ')

    setInvestigatingId(incident.id)
    setInvestigation(null)
    setInvestigationError(null)
    setSelectedIncidentId(incident.id)

    try {
      const result = await apiService.createInvestigation(question)
      setInvestigation(result)
    } catch (err) {
      setInvestigationError(getApiError(err))
    } finally {
      setInvestigatingId(null)
    }
  }

  const clearFilters = () => {
    setSearch('')
    setSeverity('all')
    setStatus('all')
  }

  const hasFilters =
    search !== '' || severity !== 'all' || status !== 'all'

  return (
    <section className="incidents-page">
      <div className="incidents-heading">
        <div>
          <div className="eyebrow">OPERATIONS / INCIDENT RESPONSE</div>
          <h1>Incident management</h1>
          <p>
            Monitor operational incidents, inspect affected resources and
            investigate issues with AI assistance.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw
            size={15}
            className={loading ? 'incident-spin' : ''}
          />
          Refresh incidents
        </button>
      </div>

      <div className="incident-notice">
        <Info size={16} />
        <span>
          <strong>Demo incident data:</strong> Incidents are supplied by
          your backend. AI investigations provide recommendations only;
          infrastructure changes require separate human approval.
        </span>
      </div>

      {error && (
        <div className="incident-error">
          <AlertTriangle size={17} />
          <span>{error}</span>
          <button onClick={onRefresh}>Retry</button>
        </div>
      )}

      <div className="incident-metrics">
        <IncidentMetric
          label="Total incidents"
          value={incidents.length}
          icon={<FileSearch size={19} />}
          tone="purple"
        />
        <IncidentMetric
          label="Open incidents"
          value={openCount}
          icon={<AlertTriangle size={19} />}
          tone="amber"
        />
        <IncidentMetric
          label="Investigating"
          value={investigatingCount}
          icon={<Activity size={19} />}
          tone="blue"
        />
        <IncidentMetric
          label="Critical incidents"
          value={criticalCount}
          icon={<ShieldAlert size={19} />}
          tone="red"
        />
      </div>

      <div className="incident-workspace">
        <section className="incident-list-panel">
          <div className="incident-panel-heading">
            <div>
              <h2>Incident queue</h2>
              <p>Review and prioritize reported incidents</p>
            </div>
            <span className="incident-api-label">API DATA</span>
          </div>

          <div className="incident-filters">
            <div className="incident-search">
              <Search size={15} />
              <input
                value={search}
                onChange={event => setSearch(event.target.value)}
                placeholder="Search incidents or resources..."
              />
            </div>

            <div className="incident-filter-row">
              <select
                value={severity}
                onChange={event =>
                  setSeverity(event.target.value as SeverityFilter)
                }
                aria-label="Filter by severity"
              >
                <option value="all">All severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <select
                value={status}
                onChange={event =>
                  setStatus(event.target.value as StatusFilter)
                }
                aria-label="Filter by status"
              >
                <option value="all">All statuses</option>
                <option value="open">Open</option>
                <option value="investigating">Investigating</option>
                <option value="resolved">Resolved</option>
              </select>

              {hasFilters && (
                <button className="incident-clear" onClick={clearFilters}>
                  Clear
                </button>
              )}
            </div>
          </div>

          <div className="incident-list-count">
            Showing <strong>{filteredIncidents.length}</strong> of{' '}
            <strong>{incidents.length}</strong> incidents
          </div>

          <div className="incident-queue">
            {filteredIncidents.length === 0 ? (
              <div className="incident-empty">
                <Search size={22} />
                <strong>No incidents found</strong>
                <span>Try changing your search or filters.</span>
              </div>
            ) : (
              filteredIncidents.map(incident => {
                const selected = selectedIncidentId === incident.id

                return (
                  <button
                    className={`incident-queue-item ${selected ? 'selected' : ''}`}
                    key={incident.id}
                    onClick={() => selectIncident(incident)}
                  >
                    <div className="incident-queue-top">
                      <span className="incident-id">{incident.id}</span>
                      <SeverityBadge severity={incident.severity} />
                    </div>

                    <strong className="incident-queue-title">
                      {incident.title}
                    </strong>

                    <div className="incident-queue-bottom">
                      <StatusBadge status={incident.status} />
                      <span>
                        {incident.affected_asset_ids.length} affected resource
                        {incident.affected_asset_ids.length === 1 ? '' : 's'}
                      </span>
                      <ChevronRight size={15} />
                    </div>
                  </button>
                )
              })
            )}
          </div>
        </section>

        <section className="incident-detail-panel">
          {!selectedIncident ? (
            <div className="incident-empty">
              <FileSearch size={26} />
              <strong>Select an incident</strong>
              <span>Choose an incident from the queue to inspect its details.</span>
            </div>
          ) : (
            <>
              <div className="incident-detail-heading">
                <div>
                  <span className="incident-id">{selectedIncident.id}</span>
                  <h2>{selectedIncident.title}</h2>
                </div>
                <SeverityBadge severity={selectedIncident.severity} />
              </div>

              <div className="incident-detail-status">
                <StatusBadge status={selectedIncident.status} />
              </div>

              <div className="incident-detail-section">
                <h3>
                  <Cloud size={16} />
                  Affected resources
                </h3>

                {selectedIncident.affected_asset_ids.length === 0 ? (
                  <p className="incident-muted">
                    No affected resource IDs were provided.
                  </p>
                ) : (
                  selectedIncident.affected_asset_ids.map(id => {
                    const asset = assetById.get(id)

                    return (
                      <div className="incident-asset" key={id}>
                        <div className="incident-asset-icon">
                          <Server size={17} />
                        </div>
                        <div className="incident-asset-copy">
                          <strong>{asset?.name ?? id}</strong>
                          <span>{id}</span>
                          {asset && (
                            <small>
                              {asset.provider} · {asset.resource_type} ·{' '}
                              {asset.region} · {asset.environment}
                            </small>
                          )}
                        </div>
                        {asset && (
                          <span className="incident-asset-cpu">
                            CPU {asset.cpu_utilization_percent.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    )
                  })
                )}
              </div>

              <div className="incident-investigate-action">
                <div>
                  <h3>
                    <Bot size={17} />
                    AI investigation
                  </h3>
                  <p>
                    Analyze this incident using the backend investigation
                    workflow.
                  </p>
                </div>

                <button
                  className="incident-ai-button"
                  onClick={() => runInvestigation(selectedIncident)}
                  disabled={investigatingId !== null}
                >
                  {investigatingId === selectedIncident.id ? (
                    <RefreshCw size={15} className="incident-spin" />
                  ) : (
                    <Bot size={16} />
                  )}
                  {investigatingId === selectedIncident.id
                    ? 'Investigating...'
                    : 'Investigate with AI'}
                </button>
              </div>

              {investigationError && (
                <div className="incident-error incident-investigation-error">
                  <AlertTriangle size={16} />
                  <span>{investigationError}</span>
                </div>
              )}

              {investigation && (
                <div className="investigation-result">
                  <div className="investigation-result-heading">
                    <div>
                      <span className="eyebrow">AI INVESTIGATION RESULT</span>
                      <h3>Investigation findings</h3>
                    </div>
                    <span className="investigation-mode">
                      {investigation.mode.replaceAll('_', ' ')}
                    </span>
                  </div>

                  <div className="investigation-id">
                    Investigation ID: {investigation.investigation_id}
                  </div>

                  <div className="investigation-summary">
                    <strong>Summary</strong>
                    <p>{investigation.summary}</p>
                  </div>

                  <div className="investigation-findings">
                    <h4>Findings</h4>
                    {investigation.findings.length === 0 ? (
                      <p className="incident-muted">No findings returned.</p>
                    ) : (
                      investigation.findings.map((finding, index) => (
                        <div className="investigation-finding" key={`${finding.title}-${index}`}>
                          <strong>{finding.title}</strong>
                          <p>{finding.detail}</p>
                          {finding.evidence.length > 0 && (
                            <ul>
                              {finding.evidence.map((evidence, evidenceIndex) => (
                                <li key={evidenceIndex}>{evidence}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))
                    )}
                  </div>

                  <div className="investigation-actions">
                    <h4>
                      <Lightbulb size={15} />
                      Recommended actions
                    </h4>
                    {investigation.recommended_actions.length === 0 ? (
                      <p className="incident-muted">No actions returned.</p>
                    ) : (
                      <ol>
                        {investigation.recommended_actions.map((action, index) => (
                          <li key={index}>{action}</li>
                        ))}
                      </ol>
                    )}
                  </div>

                  <div className="investigation-approval-notice">
                    <ShieldAlert size={17} />
                    <span>
                      {investigation.requires_human_approval
                        ? 'Human approval is required before any proposed remediation. No infrastructure changes were executed by this investigation.'
                        : 'This investigation did not flag a human approval requirement. No infrastructure changes were executed.'}
                    </span>
                  </div>

                  {investigation.disclaimer && (
                    <p className="investigation-disclaimer">
                      {investigation.disclaimer}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </section>
      </div>

      <div className="incident-footer">
        <Clock size={14} />
        Incident timestamps and historical transitions are not included in
        the current incidents API response.
      </div>
    </section>
  )
}

function IncidentMetric({
  label,
  value,
  icon,
  tone,
}: {
  label: string
  value: number
  icon: React.ReactNode
  tone: 'purple' | 'amber' | 'blue' | 'red'
}) {
  return (
    <div className="incident-metric">
      <div className="incident-metric-top">
        <span>{label}</span>
        <div className={`incident-metric-icon ${tone}`}>{icon}</div>
      </div>
      <strong>{value}</strong>
      <small>From incident API</small>
    </div>
  )
}

function SeverityBadge({ severity }: { severity: Incident['severity'] }) {
  return (
    <span className={`incident-severity ${severity}`}>
      <span />
      {severity}
    </span>
  )
}

function StatusBadge({ status }: { status: Incident['status'] }) {
  return (
    <span className={`incident-status ${status}`}>
      <span />
      {status}
    </span>
  )
}
