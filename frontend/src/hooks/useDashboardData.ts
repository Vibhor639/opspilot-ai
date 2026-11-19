
import { useCallback, useEffect, useState } from 'react'
import {
  apiService,
  getApiError,
  type Asset,
  type CostAnomaly,
  type CostSummary,
  type Incident,
  type UtilizationReport,
  type CloudConnectionStatus,
} from '../services/api'

export function useDashboardData() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null)
  const [costAnomalies, setCostAnomalies] = useState<CostAnomaly[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [utilization, setUtilization] = useState<UtilizationReport | null>(null)
  const [cloudStatus, setCloudStatus] = useState<CloudConnectionStatus | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)

    const results = await Promise.allSettled([
      apiService.getAssets(),
      apiService.getCostSummary(),
      apiService.getCostAnomalies(),
      apiService.getIncidents(),
      apiService.getUtilization(),
      apiService.getCloudStatus(),
    ])

    const errors: string[] = []

    if (results[0].status === 'fulfilled') setAssets(results[0].value)
    else errors.push(`Assets: ${getApiError(results[0].reason)}`)

    if (results[1].status === 'fulfilled') setCostSummary(results[1].value)
    else errors.push(`Costs: ${getApiError(results[1].reason)}`)

    if (results[2].status === 'fulfilled') setCostAnomalies(results[2].value)
    else errors.push(`Cost anomalies: ${getApiError(results[2].reason)}`)

    if (results[3].status === 'fulfilled') setIncidents(results[3].value)
    else errors.push(`Incidents: ${getApiError(results[3].reason)}`)

    if (results[4].status === 'fulfilled') setUtilization(results[4].value)
    else errors.push(`Utilization: ${getApiError(results[4].reason)}`)

    if (results[5].status === 'fulfilled') setCloudStatus(results[5].value)
    else errors.push(`Cloud status: ${getApiError(results[5].reason)}`)

    setError(errors.length ? errors.join(' | ') : null)
    setLastUpdated(new Date())
    setLoading(false)
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return {
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
  }
}
