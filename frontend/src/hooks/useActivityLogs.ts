import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { ActivityLog, PaginatedResponse } from '@/types'

export const useActivityLogs = (page: number = 1, size: number = 10, entityType?: string, entityId?: number) => {
  return useQuery({
    queryKey: ['activity-logs', page, size, entityType, entityId],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (entityType) {
        params.append('entity_type', entityType)
      }
      if (entityId) {
        params.append('entity_id', String(entityId))
      }
      const response = await axiosInstance.get<PaginatedResponse<ActivityLog>>(
        `${API_ENDPOINTS.ACTIVITY_LOGS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useEntityActivityLogs = (entityType: string, entityId: number) => {
  return useQuery({
    queryKey: ['activity-logs', 'entity', entityType, entityId],
    queryFn: async () => {
      const response = await axiosInstance.get<ActivityLog[]>(
        API_ENDPOINTS.ACTIVITY_LOGS_AUDIT(entityType, entityId)
      )
      return response.data
    },
    enabled: !!entityType && !!entityId,
  })
}

export const useUserActivityLogs = (userId: number, page: number = 1, size: number = 10) => {
  return useQuery({
    queryKey: ['activity-logs', 'user', userId, page, size],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      const response = await axiosInstance.get<PaginatedResponse<ActivityLog>>(
        `${API_ENDPOINTS.ACTIVITY_LOGS_USER(userId)}?${params.toString()}`
      )
      return response.data
    },
    enabled: !!userId,
  })
}

export const useRecentActivityLogs = (limit: number = 20) => {
  return useQuery({
    queryKey: ['activity-logs', 'recent', limit],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: String(limit),
      })
      const response = await axiosInstance.get<ActivityLog[]>(
        `${API_ENDPOINTS.ACTIVITY_LOGS_RECENT}?${params.toString()}`
      )
      return response.data
    },
  })
}
