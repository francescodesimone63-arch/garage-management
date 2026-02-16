import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { Tire, PaginatedResponse, TireSeason, TireCondition, TireStatus } from '@/types'

// ALLINEATO AL BACKEND MODEL
interface TireCreate {
  vehicle_id: number
  tipo_stagione: TireSeason
  marca?: string
  modello?: string
  misura?: string
  data_deposito?: string
  data_ultimo_cambio?: string
  data_prossimo_cambio?: string
  stato: TireStatus
  position?: string
  condition?: TireCondition
  tread_depth?: number
  manufacture_date?: string
  last_rotation_date?: string
  last_rotation_km?: number
  posizione_deposito?: string
  note?: string
}

export const useTires = (page: number = 1, size: number = 10, search?: string) => {
  return useQuery({
    queryKey: ['tires', page, size, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (search) {
        params.append('search', search)
      }
      const response = await axiosInstance.get<PaginatedResponse<Tire>>(
        `${API_ENDPOINTS.TIRES}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useTire = (id: number) => {
  return useQuery({
    queryKey: ['tire', id],
    queryFn: async () => {
      const response = await axiosInstance.get<Tire>(
        `${API_ENDPOINTS.TIRES}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreateTire = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: TireCreate) => {
      const response = await axiosInstance.post<Tire>(
        `${API_ENDPOINTS.TIRES}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tires'] })
      message.success('Pneumatico creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione del pneumatico')
    },
  })
}

export const useUpdateTire = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<TireCreate> }) => {
      const response = await axiosInstance.put<Tire>(
        `${API_ENDPOINTS.TIRES}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tires'] })
      queryClient.invalidateQueries({ queryKey: ['tire', variables.id] })
      message.success('Pneumatico aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento del pneumatico')
    },
  })
}

export const useDeleteTire = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.TIRES}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tires'] })
      message.success('Pneumatico eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione del pneumatico')
    },
  })
}

export const useVehicleTires = (vehicleId: number) => {
  return useQuery({
    queryKey: ['tires', 'vehicle', vehicleId],
    queryFn: async () => {
      const response = await axiosInstance.get<Tire[]>(
        `${API_ENDPOINTS.TIRES}/vehicle/${vehicleId}`
      )
      return response.data
    },
    enabled: !!vehicleId,
  })
}
