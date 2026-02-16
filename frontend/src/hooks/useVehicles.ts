import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { Vehicle, PaginatedResponse } from '@/types'

interface VehicleCreate {
  customer_id: number
  targa: string
  marca: string
  modello: string
  anno: number
  telaio?: string
  colore?: string
  km_attuali?: number
  note?: string
  // Campi tecnici aggiuntivi
  cilindrata?: string
  kw?: number
  cv?: number
  porte?: number
  carburante?: string
  prima_immatricolazione?: string
}

export const useVehicles = (page: number = 1, size: number = 10, search?: string) => {
  return useQuery({
    queryKey: ['vehicles', page, size, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (search) {
        params.append('search', search)
      }
      const response = await axiosInstance.get<PaginatedResponse<Vehicle>>(
        `${API_ENDPOINTS.VEHICLES}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useVehicle = (id: number) => {
  return useQuery({
    queryKey: ['vehicle', id],
    queryFn: async () => {
      const response = await axiosInstance.get<Vehicle>(
        `${API_ENDPOINTS.VEHICLES}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCustomerVehicles = (customerId: number) => {
  return useQuery({
    queryKey: ['customer-vehicles', customerId],
    queryFn: async () => {
      const response = await axiosInstance.get<Vehicle[]>(
        `${API_ENDPOINTS.CUSTOMERS}/${customerId}/vehicles`
      )
      return response.data
    },
    enabled: !!customerId,
  })
}

export const useCreateVehicle = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: VehicleCreate) => {
      const response = await axiosInstance.post<Vehicle>(
        `${API_ENDPOINTS.VEHICLES}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      message.success('Veicolo creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione del veicolo')
    },
  })
}

export const useUpdateVehicle = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<VehicleCreate> }) => {
      const response = await axiosInstance.put<Vehicle>(
        `${API_ENDPOINTS.VEHICLES}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      queryClient.invalidateQueries({ queryKey: ['vehicle', variables.id] })
      message.success('Veicolo aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento del veicolo')
    },
  })
}

export const useDeleteVehicle = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.VEHICLES}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] })
      message.success('Veicolo eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione del veicolo')
    },
  })
}
