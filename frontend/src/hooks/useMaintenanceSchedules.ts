import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { MaintenanceSchedule, PaginatedResponse, MaintenanceType, MaintenanceStatus } from '@/types'

// ALLINEATO AL BACKEND MODEL
interface MaintenanceScheduleCreate {
  vehicle_id: number
  tipo: MaintenanceType
  descrizione: string
  km_scadenza?: number
  data_scadenza?: string
  km_preavviso?: number
  giorni_preavviso?: number
  stato?: MaintenanceStatus
  ricorrente?: boolean
  intervallo_km?: number
  intervallo_giorni?: number
  ultima_notifica?: string
  note?: string
}

export const useMaintenanceSchedules = (page: number = 1, size: number = 10, vehicleId?: number) => {
  return useQuery({
    queryKey: ['maintenance-schedules', page, size, vehicleId],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (vehicleId) {
        params.append('vehicle_id', String(vehicleId))
      }
      const response = await axiosInstance.get<PaginatedResponse<MaintenanceSchedule>>(
        `${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useMaintenanceSchedule = (id: number) => {
  return useQuery({
    queryKey: ['maintenance-schedule', id],
    queryFn: async () => {
      const response = await axiosInstance.get<MaintenanceSchedule>(
        `${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreateMaintenanceSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: MaintenanceScheduleCreate) => {
      const response = await axiosInstance.post<MaintenanceSchedule>(
        `${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-schedules'] })
      message.success('Pianificazione manutenzione creata con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione della pianificazione')
    },
  })
}

export const useUpdateMaintenanceSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<MaintenanceScheduleCreate> }) => {
      const response = await axiosInstance.put<MaintenanceSchedule>(
        `${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['maintenance-schedule', variables.id] })
      message.success('Pianificazione manutenzione aggiornata con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento della pianificazione')
    },
  })
}

export const useDeleteMaintenanceSchedule = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-schedules'] })
      message.success('Pianificazione manutenzione eliminata con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione della pianificazione')
    },
  })
}

export const useUpcomingMaintenances = () => {
  return useQuery({
    queryKey: ['maintenance-schedules', 'upcoming'],
    queryFn: async () => {
      const response = await axiosInstance.get<MaintenanceSchedule[]>(
        `${API_ENDPOINTS.MAINTENANCE_SCHEDULES}/upcoming`
      )
      return response.data
    },
  })
}
