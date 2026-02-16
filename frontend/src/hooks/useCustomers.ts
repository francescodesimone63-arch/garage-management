import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { Customer, CustomerCreate, PaginatedResponse } from '@/types'

export const useCustomers = (page: number = 1, size: number = 10, search?: string) => {
  return useQuery({
    queryKey: ['customers', page, size, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (search) {
        params.append('search', search)
      }
      const response = await axiosInstance.get<PaginatedResponse<Customer>>(
        `${API_ENDPOINTS.CUSTOMERS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const useCustomer = (id: number) => {
  return useQuery({
    queryKey: ['customer', id],
    queryFn: async () => {
      const response = await axiosInstance.get<Customer>(
        `${API_ENDPOINTS.CUSTOMERS}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreateCustomer = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CustomerCreate) => {
      const response = await axiosInstance.post<Customer>(
        `${API_ENDPOINTS.CUSTOMERS}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      message.success('Cliente creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione del cliente')
    },
  })
}

export const useUpdateCustomer = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<CustomerCreate> }) => {
      const response = await axiosInstance.put<Customer>(
        `${API_ENDPOINTS.CUSTOMERS}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      queryClient.invalidateQueries({ queryKey: ['customer', variables.id] })
      message.success('Cliente aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento del cliente')
    },
  })
}

export const useDeleteCustomer = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.CUSTOMERS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      message.success('Cliente eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione del cliente')
    },
  })
}
