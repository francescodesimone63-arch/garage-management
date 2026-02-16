import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { CourtesyCar, PaginatedResponse, ContractType, CourtesyCarStatus } from '@/types'

// ALLINEATO AL BACKEND MODEL
interface CourtesyCarCreate {
  vehicle_id: number
  contratto_tipo: ContractType
  fornitore_contratto?: string
  data_inizio_contratto?: string
  data_scadenza_contratto?: string
  canone_mensile?: number
  km_inclusi_anno?: number
  stato: CourtesyCarStatus
  note?: string
}

export const useCourtesyCars = (page: number = 1, size: number = 10, search?: string, stato?: string) => {
  return useQuery({
    queryKey: ['courtesy-cars', page, size, search, stato],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (search) {
        params.append('search', search)
      }
      if (stato) {
        params.append('stato_filter', stato)
      }
      const response = await axiosInstance.get<PaginatedResponse<CourtesyCar>>(
        `${API_ENDPOINTS.COURTESY_CARS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useCourtesyCar = (id: number) => {
  return useQuery({
    queryKey: ['courtesy-car', id],
    queryFn: async () => {
      const response = await axiosInstance.get<CourtesyCar>(
        `${API_ENDPOINTS.COURTESY_CARS}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreateCourtesyCar = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CourtesyCarCreate) => {
      const response = await axiosInstance.post<CourtesyCar>(
        `${API_ENDPOINTS.COURTESY_CARS}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courtesy-cars'] })
      message.success('Auto cortesia creata con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione dell\'auto cortesia')
    },
  })
}

export const useUpdateCourtesyCar = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<CourtesyCarCreate> }) => {
      const response = await axiosInstance.put<CourtesyCar>(
        `${API_ENDPOINTS.COURTESY_CARS}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['courtesy-cars'] })
      queryClient.invalidateQueries({ queryKey: ['courtesy-car', variables.id] })
      message.success('Auto cortesia aggiornata con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento dell\'auto cortesia')
    },
  })
}

export const useDeleteCourtesyCar = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.COURTESY_CARS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courtesy-cars'] })
      message.success('Auto cortesia eliminata con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione dell\'auto cortesia')
    },
  })
}

export const useAvailableCourtesyCars = () => {
  return useQuery({
    queryKey: ['courtesy-cars', 'available'],
    queryFn: async () => {
      const response = await axiosInstance.get<CourtesyCar[]>(
        `${API_ENDPOINTS.COURTESY_CARS}/available`
      )
      return response.data
    },
  })
}
