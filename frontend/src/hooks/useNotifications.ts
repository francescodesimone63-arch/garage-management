import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { Notification, PaginatedResponse } from '@/types'

export const useNotifications = (page: number = 1, size: number = 10) => {
  return useQuery({
    queryKey: ['notifications', page, size],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      const response = await axiosInstance.get<PaginatedResponse<Notification>>(
        `${API_ENDPOINTS.NOTIFICATIONS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useUnreadNotificationsCount = () => {
  return useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: async () => {
      const response = await axiosInstance.get<{ count: number }>(
        API_ENDPOINTS.NOTIFICATIONS_UNREAD_COUNT
      )
      return response.data.count
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export const useMarkNotificationAsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.patch(API_ENDPOINTS.NOTIFICATIONS_READ(id))
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications', 'unread-count'] })
    },
  })
}

export const useMarkAllNotificationsAsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      await axiosInstance.post(API_ENDPOINTS.NOTIFICATIONS_MARK_READ)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notifications', 'unread-count'] })
      message.success('Tutte le notifiche sono state contrassegnate come lette')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento delle notifiche')
    },
  })
}

export const useDeleteNotification = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.NOTIFICATIONS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      message.success('Notifica eliminata con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione della notifica')
    },
  })
}
