import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { WorkOrder, PaginatedResponse } from '@/types'

// ALLINEATO AL BACKEND SCHEMA
interface WorkOrderCreate {
  vehicle_id: number
  customer_id: number
  numero_scheda: string
  data_appuntamento: string
  data_fine_prevista?: string
  data_completamento?: string
  tipo_danno?: string
  priorita?: string
  valutazione_danno: string
  note?: string
  stato?: string
  creato_da?: number
  approvato_da?: number
  auto_cortesia_id?: number
  costo_stimato?: number
  costo_finale?: number
}

export const useWorkOrders = (page: number = 1, size: number = 10, search?: string, status?: string) => {
  return useQuery({
    queryKey: ['work-orders', page, size, search, status],
    queryFn: async () => {
      try {
        const params = new URLSearchParams({
          skip: String((page - 1) * size),
          limit: String(size),
        })
        if (search) {
          params.append('search', search)
        }
        if (status) {
          params.append('stato', status)  // ALLINEATO AL BACKEND: 'status' -> 'stato'
        }
        const url = `${API_ENDPOINTS.WORK_ORDERS}/?${params.toString()}`
        console.log('🔍 Loading work orders from:', url)
        const response = await axiosInstance.get<PaginatedResponse<WorkOrder>>(url)
        console.log('✅ Work orders loaded:', response.data.items.length, 'items')
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading work orders:', error)
        if (error.response) {
          console.error('Response status:', error.response.status)
          console.error('Response data:', error.response.data)
        }
        throw error
      }
    },
    retry: 1,
    staleTime: 0,  // Reload immediately when refocused
  })
}

export const useWorkOrder = (id: number) => {
  return useQuery({
    queryKey: ['work-order', id],
    queryFn: async () => {
      console.log('📥 Loading work order:', id)
      try {
        const response = await axiosInstance.get<WorkOrder>(
          `${API_ENDPOINTS.WORK_ORDERS}/${id}`
        )
        console.log('✅ Work order loaded:', response.data.numero_scheda)
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading work order:', error.message)
        throw error
      }
    },
    enabled: !!id,
    retry: 1,
    staleTime: 0,  // Always fetch fresh data
  })
}

export const useCreateWorkOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: WorkOrderCreate) => {
      const response = await axiosInstance.post<WorkOrder>(
        `${API_ENDPOINTS.WORK_ORDERS}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] })
      message.success('Ordine di lavoro creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione dell\'ordine di lavoro')
    },
  })
}

export const useUpdateWorkOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<WorkOrderCreate> }) => {
      const response = await axiosInstance.put<WorkOrder>(
        `${API_ENDPOINTS.WORK_ORDERS}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] })
      queryClient.invalidateQueries({ queryKey: ['work-order', variables.id] })
      message.success('Ordine di lavoro aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento dell\'ordine di lavoro')
    },
  })
}

export const useDeleteWorkOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.WORK_ORDERS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] })
      message.success('Ordine di lavoro eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione dell\'ordine di lavoro')
    },
  })
}
