import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { CalendarEvent, PaginatedResponse } from '@/types'

interface CalendarEventCreate {
  title: string
  description?: string
  event_type: string
  start_datetime: string
  end_datetime?: string
  all_day?: boolean
  location?: string
  related_entity_type?: string
  related_entity_id?: number
  assigned_to_id?: number
  reminder_before_minutes?: number
  is_recurring?: boolean
  recurrence_rule?: string
}

export const useCalendarEvents = (page: number = 1, size: number = 10, startDate?: string, endDate?: string) => {
  return useQuery({
    queryKey: ['calendar-events', page, size, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (startDate) {
        params.append('start_date', startDate)
      }
      if (endDate) {
        params.append('end_date', endDate)
      }
      const response = await axiosInstance.get<PaginatedResponse<CalendarEvent>>(
        `${API_ENDPOINTS.CALENDAR_EVENTS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useCalendarEvent = (id: number) => {
  return useQuery({
    queryKey: ['calendar-event', id],
    queryFn: async () => {
      const response = await axiosInstance.get<CalendarEvent>(
        `${API_ENDPOINTS.CALENDAR_EVENTS}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreateCalendarEvent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CalendarEventCreate) => {
      const response = await axiosInstance.post<CalendarEvent>(
        `${API_ENDPOINTS.CALENDAR_EVENTS}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar-events'] })
      message.success('Evento calendario creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione dell\'evento')
    },
  })
}

export const useUpdateCalendarEvent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<CalendarEventCreate> }) => {
      const response = await axiosInstance.put<CalendarEvent>(
        `${API_ENDPOINTS.CALENDAR_EVENTS}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['calendar-events'] })
      queryClient.invalidateQueries({ queryKey: ['calendar-event', variables.id] })
      message.success('Evento calendario aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento dell\'evento')
    },
  })
}

export const useDeleteCalendarEvent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.CALENDAR_EVENTS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar-events'] })
      message.success('Evento calendario eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione dell\'evento')
    },
  })
}
