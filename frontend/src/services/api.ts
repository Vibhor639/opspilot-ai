
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Asset {
  id: string
  name: string
  provider: 'AWS' | 'GCP'
  resource_type: string
  region: string
  monthly_cost: number
  previous_monthly_cost: number
  cpu_utilization_percent: number
  memory_utilization_percent: number
  environment: 'production' | 'staging' | 'development'
  owner_team: string
  tags: Record<string, string>
}

export interface CostService {
  service: string
  current_month: number
  previous_month: number
  change_amount: number
  change_percent: number
}

export interface CostSummary {
  currency: string
  current_month: number
  previous_month: number
  change_amount: number
  change_percent: number
  services: CostService[]
}

export interface CostAnomaly {
  service: string
  current_month: number
  previous_month: number
  change_amount: number
  change_percent: number
  severity: 'medium' | 'high'
  explanation: string
}

export interface Incident {
  id: string
  title: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'investigating' | 'resolved'
  affected_asset_ids: string[]
}

export interface UtilizationItem {
  asset_id: string
  asset_name: string
  resource_type: string
  cpu_utilization_percent: number
  memory_utilization_percent: number
  classification: 'underutilized' | 'healthy' | 'overutilized'
  recommendation: string
}

export interface UtilizationReport {
  total_assets: number
  underutilized: number
  healthy: number
  overutilized: number
  items: UtilizationItem[]
}

export interface InvestigationFinding {
  title: string
  detail: string
  evidence: string[]
}

export interface InvestigationResult {
  investigation_id: string
  question: string
  summary: string
  findings: InvestigationFinding[]
  recommended_actions: string[]
  requires_human_approval: boolean
  mode: string
  disclaimer: string
}

export interface AgentTraceItem {
  agent: string
  status: string
  detail: string
  timestamp: string
}

export interface AgentInvestigationResult {
  thread_id: string
  question: string
  route: string
  answer: string
  recommended_actions: string[]
  requires_human_approval: boolean
  trace: AgentTraceItem[]
  warning: string
  reasoning_mode: string
  selected_agents: string[]
  planning_rationale: string
  model: string | null
}

export interface CloudConnectionStatus {
  [key: string]: unknown
}

export const apiService = {
  getAssets: async () => {
    const response = await api.get<Asset[]>('/assets')
    return response.data
  },

  getCostSummary: async () => {
    const response = await api.get<CostSummary>('/costs/summary')
    return response.data
  },

  getCostAnomalies: async () => {
    const response = await api.get<CostAnomaly[]>('/costs/anomalies')
    return response.data
  },

  getIncidents: async () => {
    const response = await api.get<Incident[]>('/incidents')
    return response.data
  },

  getUtilization: async () => {
    const response = await api.get<UtilizationReport>('/utilization')
    return response.data
  },

    createInvestigation: async (question: string) => {
    const response = await api.post<InvestigationResult>(
      '/investigations',
      { question },
    )
    return response.data
  },

  runAgentInvestigation: async (
  question: string,
  threadId?: string,
) => {
  const response = await api.post<AgentInvestigationResult>(
    '/agents/investigate',
    {
      question,
      ...(threadId ? { thread_id: threadId } : {}),
    },
  )
  return response.data
},

getAgentRun: async (threadId: string) => {
  const response = await api.get<AgentInvestigationResult>(
    `/agents/runs/${encodeURIComponent(threadId)}`,
  )
  return response.data
},

  getCloudStatus: async () => {
    const response = await api.get<CloudConnectionStatus>('/cloud/live/status')
    return response.data
  },
}

export function getApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail
      || error.message
      || 'Unable to connect to the backend.'
  }

  return error instanceof Error ? error.message : 'An unexpected error occurred.'
}

export default api
