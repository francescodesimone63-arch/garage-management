import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { DashboardSummary } from '@/types'

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: async () => {
      const response = await axiosInstance.get<DashboardSummary>(
        API_ENDPOINTS.DASHBOARD_SUMMARY
      )
      return response.data
    },
    refetchInterval: 60000, // Refresh every minute
  })
}

export const useDashboardAlerts = () => {
  return useQuery({
    queryKey: ['dashboard', 'alerts'],
    queryFn: async () => {
      const response = await axiosInstance.get<any[]>(
        API_ENDPOINTS.DASHBOARD_ALERTS
      )
      return response.data
    },
    refetchInterval: 60000, // Refresh every minute
  })
}

export const useDashboardRecentActivity = (limit: number = 10) => {
  return useQuery({
    queryKey: ['dashboard', 'recent-activity', limit],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: String(limit),
      })
      const response = await axiosInstance.get<any[]>(
        `${API_ENDPOINTS.DASHBOARD_RECENT_ACTIVITY}?${params.toString()}`
      )
      return response.data
    },
  })
}
