import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { InterventionStatusType } from '@/types'

export interface SystemTableItem {
  id: number
  nome: string
  descrizione?: string
  attivo: boolean
  created_at?: string
  updated_at?: string
}

export const useDamageTypes = () => {
  return useQuery({
    queryKey: ['damage-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<SystemTableItem[]>(
        API_ENDPOINTS.SYSTEM_DAMAGE_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}

export const useCustomerTypes = () => {
  return useQuery({
    queryKey: ['customer-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<SystemTableItem[]>(
        API_ENDPOINTS.SYSTEM_CUSTOMER_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}

export const useWorkOrderStatusTypes = () => {
  return useQuery({
    queryKey: ['work-order-status-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<SystemTableItem[]>(
        API_ENDPOINTS.SYSTEM_WORKORDER_STATUS_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}

export const usePriorityTypes = () => {
  return useQuery({
    queryKey: ['priority-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<SystemTableItem[]>(
        API_ENDPOINTS.SYSTEM_PRIORITY_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}

export const useInterventionStatusTypes = () => {
  return useQuery({
    queryKey: ['intervention-status-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<InterventionStatusType[]>(
        API_ENDPOINTS.SYSTEM_INTERVENTION_STATUS_TYPES
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5, // 5 minuti
    gcTime: 1000 * 60 * 10, // 10 minuti (ex: cacheTime)
  })
}
