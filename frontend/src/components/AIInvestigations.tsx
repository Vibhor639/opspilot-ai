
import { useState } from 'react'
import {
  Bot,
  Brain,
  Clock,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Activity,
} from 'lucide-react'
import { apiService, getApiError } from '../services/api'
import type { AgentInvestigationResult } from '../services/api'
import './AIInvestigations.css'

const suggestedPrompts = [
  'Investigate the open incidents and identify the highest-priority operational risks.',
  'Investigate the recent increase in cloud infrastructure costs.',
  'Find underutilized cloud resources and recommend cost optimizations.',
  'Analyze production resource utilization and identify potential bottlenecks.',
]

export function AIInvestigations() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<AgentInvestigationResult | null>(null)
  const [history, setHistory] = useState<AgentInvestigationResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [threadId, setThreadId] = useState('')

  const runInvestigation = async () => {
    if (question.trim().length < 3 || loading) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await apiService.runAgentInvestigation(question.trim())
      setResult(response)
      setThreadId(response.thread_id)
      setHistory((previous) => [
        response,
        ...previous.filter((item) => item.thread_id !== response.thread_id),
      ])
    } catch (err) {
      setError(getApiError(err))
    } finally {
      setLoading(false)
    }
  }

  const loadPreviousRun = async (id: string) => {
    setLoading(true)
    setError('')

    try {
      const response = await apiService.getAgentRun(id)
      setResult(response)
      setThreadId(response.thread_id)
      setQuestion(response.question)
    } catch (err) {
      setError(getApiError(err))
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (value: string) => {
    const date = new Date(value)
    return Number.isNaN(date.getTime())
      ? value
      : date.toLocaleString()
  }

  return (
    <div className="ai-investigations">
      <div className="ai-page-heading">
        <div>
          <div className="ai-eyebrow">
            <Sparkles size={14} /> INTELLIGENT OPERATIONS
          </div>
          <h2>AI Investigations</h2>
          <p>
            Investigate cloud and operational issues using a coordinated
            team of specialist AI agents.
          </p>
        </div>

        <div className="ai-status">
          <span className="ai-status-dot" />
          Agent system available
        </div>
      </div>

      <div className="ai-workspace">
        <section className="ai-main-column">
          <div className="ai-query-card">
            <div className="ai-card-heading">
              <div className="ai-heading-icon">
                <Brain size={20} />
              </div>
              <div>
                <h3>Start an investigation</h3>
                <p>Describe the operational issue you want to investigate.</p>
              </div>
            </div>

            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Example: Investigate why production cloud costs have increased and identify the resources responsible..."
              rows={5}
              disabled={loading}
            />

            <div className="ai-query-footer">
              <span>{question.length}/2000 characters</span>
              <button
                className="ai-run-button"
                onClick={runInvestigation}
                disabled={loading || question.trim().length < 3}
              >
                {loading ? (
                  <RefreshCw size={16} className="ai-spin" />
                ) : (
                  <Play size={16} />
                )}
                {loading ? 'Investigating...' : 'Run investigation'}
              </button>
            </div>

            {error && (
              <div className="ai-error">
                <AlertTriangle size={17} />
                {error}
              </div>
            )}
          </div>

          <div className="ai-prompts-section">
            <h3>Suggested investigations</h3>
            <div className="ai-prompt-grid">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  className="ai-prompt"
                  onClick={() => setQuestion(prompt)}
                  disabled={loading}
                >
                  <Sparkles size={15} />
                  <span>{prompt}</span>
                  <ChevronRight size={15} />
                </button>
              ))}
            </div>
          </div>

          {result && (
            <div className="ai-result">
              <div className="ai-result-heading">
                <div>
                  <div className="ai-eyebrow">INVESTIGATION RESULT</div>
                  <h3>Investigation completed</h3>
                </div>
                <span className="ai-completed">
                  <CheckCircle2 size={15} /> Completed
                </span>
              </div>

              <div className="ai-result-meta">
                <span><Activity size={14} /> Route: {result.route}</span>
                <span><Brain size={14} /> Mode: {result.reasoning_mode}</span>
                {result.model && <span>Model: {result.model}</span>}
              </div>

              <div className="ai-answer">
                <h4>Analysis</h4>
                <p>{result.answer}</p>
              </div>

              {result.planning_rationale && (
                <div className="ai-detail-block">
                  <h4>Planning rationale</h4>
                  <p>{result.planning_rationale}</p>
                </div>
              )}

              {result.selected_agents.length > 0 && (
                <div className="ai-detail-block">
                  <h4>Selected specialist agents</h4>
                  <div className="ai-agent-chips">
                    {result.selected_agents.map((agent) => (
                      <span key={agent}>{agent}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.recommended_actions.length > 0 && (
                <div className="ai-detail-block">
                  <h4>Recommended actions</h4>
                  <ul className="ai-recommendations">
                    {result.recommended_actions.map((action, index) => (
                      <li key={`${index}-${action}`}>
                        <CheckCircle2 size={16} />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="ai-approval-notice">
                <ShieldCheck size={19} />
                <div>
                  <strong>
                    {result.requires_human_approval
                      ? 'Human approval required'
                      : 'No approval requirement reported'}
                  </strong>
                  <p>
                    This investigation is read-only. No infrastructure
                    changes are executed.
                  </p>
                </div>
              </div>

              <div className="ai-trace">
                <h4><Activity size={17} /> Agent execution trace</h4>
                {result.trace.map((item, index) => (
                  <div className="ai-trace-item" key={`${item.agent}-${index}`}>
                    <div className="ai-trace-marker">
                      <CheckCircle2 size={16} />
                    </div>
                    <div className="ai-trace-content">
                      <div className="ai-trace-title">
                        <strong>{item.agent}</strong>
                        <span>{item.status}</span>
                      </div>
                      <p>{item.detail}</p>
                      <small>{formatDate(item.timestamp)}</small>
                    </div>
                  </div>
                ))}
              </div>

              <div className="ai-thread-id">
                <span>Thread ID: {result.thread_id}</span>
                <button onClick={() => navigator.clipboard.writeText(result.thread_id)}>
                  Copy ID
                </button>
              </div>

              <div className="ai-warning">
                <AlertTriangle size={16} />
                {result.warning}
              </div>
            </div>
          )}
        </section>

        <aside className="ai-sidebar">
          <div className="ai-history-card">
            <div className="ai-history-heading">
              <h3><Clock size={17} /> Recent investigations</h3>
              <span>{history.length}</span>
            </div>

            {history.length === 0 ? (
              <div className="ai-empty-history">
                <Bot size={28} />
                <p>No investigations yet.</p>
                <span>Your recent runs will appear here.</span>
              </div>
            ) : (
              <div className="ai-history-list">
                {history.map((item) => (
                  <button
                    key={item.thread_id}
                    className={`ai-history-item ${
                      threadId === item.thread_id ? 'active' : ''
                    }`}
                    onClick={() => loadPreviousRun(item.thread_id)}
                    disabled={loading}
                  >
                    <span className="ai-history-icon">
                      <Activity size={16} />
                    </span>
                    <span className="ai-history-text">
                      <strong>{item.question}</strong>
                      <small>{item.reasoning_mode}</small>
                    </span>
                    <ChevronRight size={15} />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="ai-info-card">
            <ShieldCheck size={21} />
            <h3>Controlled operations</h3>
            <p>
              Investigations analyze available data and produce
              recommendations. Infrastructure remediation is not
              automatically executed.
            </p>
          </div>

          <div className="ai-info-card">
            <Brain size={21} />
            <h3>Agent reasoning</h3>
            <p>
              The system uses a deterministic fallback unless LLM
              reasoning is configured on the backend.
            </p>
          </div>

          <div className="ai-history-disclaimer">
            <Clock size={14} />
            Run history is held in backend memory and is cleared when the
            backend restarts.
          </div>
        </aside>
      </div>
    </div>
  )
}
