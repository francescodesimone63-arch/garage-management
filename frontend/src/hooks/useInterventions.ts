import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import type { Intervention, InterventionCreate, InterventionUpdate } from '@/types'

const API_BASE = '/work-orders'

/**
 * Hook per gestire le operazioni CRUD degli interventi
 */
export const useInterventions = (workOrderId?: number) => {
  const queryClient = useQueryClient()

  // List interventions for a work order
  const { data: interventions, isLoading, refetch, error: interventionsError } = useQuery({
    queryKey: ['interventions', workOrderId],
    queryFn: async () => {
      if (!workOrderId) return []
      console.log('📥 Loading interventions for work order:', workOrderId)
      try {
        const response = await axiosInstance.get<Intervention[]>(
          `${API_BASE}/${workOrderId}/interventions`
        )
        console.log('✅ Interventions loaded:', response.data.length)
        return response.data
      } catch (error: any) {
        console.error('❌ Error loading interventions:', error.message)
        if (error.response?.status === 404) {
          console.warn('⚠️ Work order not found for interventions:', workOrderId)
          return []
        }
        throw error
      }
    },
    enabled: !!workOrderId,
    retry: 1,  // Only retry once
    staleTime: 0  // Always fetch fresh data
  })

  // Create intervention
  const createMutation = useMutation({
    mutationFn: async ({
      workOrderId: woid,
      data
    }: {
      workOrderId: number
      data: InterventionCreate
    }) => {
      const response = await axiosInstance.post<Intervention>(
        `${API_BASE}/${woid}/interventions`,
        data
      )
      return response.data
    },
    onSuccess: (newIntervention) => {
      // Add to cache
      queryClient.setQueryData(
        ['interventions', newIntervention.work_order_id],
        (old: Intervention[] | undefined) => {
          if (!old) return [newIntervention]
          return [...old, newIntervention].sort(
            (a, b) => a.progressivo - b.progressivo
          )
        }
      )
    }
  })

  // Update intervention
  const updateMutation = useMutation({
    mutationFn: async ({
      interventionId,
      data
    }: {
      interventionId: number
      data: InterventionUpdate
    }) => {
      const response = await axiosInstance.put<Intervention>(
        `${API_BASE}/${data.work_order_id}/interventions/${interventionId}`,
        data
      )
      return response.data
    },
    onSuccess: (updatedIntervention) => {
      // Update cache
      queryClient.setQueryData(
        ['interventions', updatedIntervention.work_order_id],
        (old: Intervention[] | undefined) => {
          if (!old) return [updatedIntervention]
          return old
            .map((i) =>
              i.id === updatedIntervention.id ? updatedIntervention : i
            )
            .sort((a, b) => a.progressivo - b.progressivo)
        }
      )
    }
  })

  // Delete intervention
  const deleteMutation = useMutation({
    mutationFn: async ({
      interventionId,
      workOrderId
    }: {
      interventionId: number
      workOrderId: number
    }) => {
      await axiosInstance.delete(
        `${API_BASE}/${workOrderId}/interventions/${interventionId}`
      )
      return interventionId
    },
    onSuccess: (deletedId, { workOrderId }) => {
      // Remove from cache
      queryClient.setQueryData(
        ['interventions', workOrderId],
        (old: Intervention[] | undefined) => {
          if (!old) return []
          return old.filter((i) => i.id !== deletedId)
        }
      )
    }
  })

  return {
    interventions: interventions || [],
    isLoading,
    refetch,
    create: createMutation,
    update: updateMutation,
    delete: deleteMutation
  }
}

// Hook per creare un nuovo intervento
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
      const response = await axiosInstance.post<Intervention>(
        `${API_BASE}/${workOrderId}/interventions`,
        data
      )
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['work-orders'] })
      queryClient.invalidateQueries({
        queryKey: ['interventions', data.work_order_id]
      })
    }
  })
}
