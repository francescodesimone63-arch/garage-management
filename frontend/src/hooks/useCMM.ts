import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { CMMWorkOrderSummary, InterventionStatusUpdate, Intervention, InterventionCreate, CMMDashboardStats } from '@/types'

/**
 * Hook per gestire le work orders per il ruolo CMM (Capo Meccanica)
 */
export const useCMMWorkOrders = () => {
  return useQuery({
    queryKey: ['cmm-work-orders'],
    queryFn: async () => {
      console.log('📥 Loading CMM work orders...')
      try {
        const response = await axiosInstance.get<CMMWorkOrderSummary[]>(
          API_ENDPOINTS.CMM_WORK_ORDERS
        )
        console.log('✅ CMM Work orders loaded:', response.data.length)
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading CMM work orders:', error.message)
        throw error
      }
    },
    staleTime: 1000 * 30, // 30 secondi
  })
}

/**
 * Hook per ottenere il dettaglio di una work order CMM
 */
export const useCMMWorkOrderDetail = (workOrderId?: number) => {
  return useQuery({
    queryKey: ['cmm-work-order', workOrderId],
    queryFn: async () => {
      if (!workOrderId) return null
      console.log('📥 Loading CMM work order detail:', workOrderId)
      try {
        const response = await axiosInstance.get<CMMWorkOrderSummary>(
          API_ENDPOINTS.CMM_WORK_ORDER_DETAIL(workOrderId)
        )
        console.log('✅ CMM Work order detail loaded:', response.data.numero_scheda)
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading CMM work order detail:', error.message)
        throw error
      }
    },
    enabled: !!workOrderId,
    staleTime: 1000 * 30, // 30 secondi
  })
}

/**
 * Hook per aggiornare lo stato di un intervento (CMM/CBM)
 */
export const useUpdateInterventionStatus = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({
      workOrderId,
      interventionId,
      data
    }: {
      workOrderId: number
      interventionId: number
      data: InterventionStatusUpdate
    }) => {
      console.log('📤 Updating intervention status:', { workOrderId, interventionId, data })
      const response = await axiosInstance.patch<Intervention>(
        API_ENDPOINTS.INTERVENTION_STATUS(workOrderId, interventionId),
        data
      )
      return response.data
    },
    onSuccess: (updatedIntervention, variables) => {
      console.log('✅ Intervention status updated:', updatedIntervention)
      // Invalida le query per aggiornare i dati
      queryClient.invalidateQueries({ queryKey: ['cmm-work-orders'] })
      queryClient.invalidateQueries({ queryKey: ['cmm-work-order', variables.workOrderId] })
      queryClient.invalidateQueries({ queryKey: ['interventions', variables.workOrderId] })
    },
    onError: (error: any) => {
      console.error('❌ Error updating intervention status:', error.message)
    }
  })
}

/**
 * Hook per creare un nuovo intervento
 */
export const useCreateIntervention = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({
      workOrderId,
      data
    }: {
      workOrderId: number
      data: InterventionCreate
    }) => {
      console.log('📤 Creating intervention:', { workOrderId, data })
      const response = await axiosInstance.post<Intervention>(
        API_ENDPOINTS.CREATE_INTERVENTION(workOrderId),
        data
      )
      return response.data
    },
    onSuccess: (newIntervention, variables) => {
      console.log('✅ Intervention created:', newIntervention)
      // Invalida le query per aggiornare i dati
      queryClient.invalidateQueries({ queryKey: ['cmm-work-orders'] })
      queryClient.invalidateQueries({ queryKey: ['cmm-work-order', variables.workOrderId] })
      queryClient.invalidateQueries({ queryKey: ['interventions', variables.workOrderId] })
      queryClient.invalidateQueries({ queryKey: ['cmm-stats'] })
    },
    onError: (error: any) => {
      console.error('❌ Error creating intervention:', error.message)
    }
  })
}

/**
 * Hook per ottenere le statistiche dashboard CMM
 */
export const useCMMStats = () => {
  return useQuery({
    queryKey: ['cmm-stats'],
    queryFn: async () => {
      console.log('📥 Loading CMM stats...')
      try {
        const response = await axiosInstance.get<CMMDashboardStats>(
          API_ENDPOINTS.CMM_STATS
        )
        console.log('✅ CMM stats loaded:', response.data)
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading CMM stats:', error.message)
        throw error
      }
    },
    staleTime: 1000 * 30, // 30 secondi
  })
}
