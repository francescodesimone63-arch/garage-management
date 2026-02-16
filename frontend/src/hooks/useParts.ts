import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { message } from 'antd'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { Part, PaginatedResponse } from '@/types'

// ALLINEATO AL BACKEND MODEL
interface PartCreate {
  codice: string
  nome: string
  descrizione?: string
  categoria?: string
  marca?: string
  modello?: string
  quantita: number
  quantita_minima: number
  prezzo_acquisto?: number
  prezzo_vendita?: number
  fornitore?: string
  posizione_magazzino?: string
  tipo: string
  unita_misura?: string
  note?: string
}

export const useParts = (page: number = 1, size: number = 10, search?: string) => {
  return useQuery({
    queryKey: ['parts', page, size, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String((page - 1) * size),
        limit: String(size),
      })
      if (search) {
        params.append('search', search)
      }
      const response = await axiosInstance.get<PaginatedResponse<Part>>(
        `${API_ENDPOINTS.PARTS}/?${params.toString()}`
      )
      return response.data
    },
  })
}

export const usePart = (id: number) => {
  return useQuery({
    queryKey: ['part', id],
    queryFn: async () => {
      const response = await axiosInstance.get<Part>(
        `${API_ENDPOINTS.PARTS}/${id}`
      )
      return response.data
    },
    enabled: !!id,
  })
}

export const useCreatePart = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: PartCreate) => {
      const response = await axiosInstance.post<Part>(
        `${API_ENDPOINTS.PARTS}/`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parts'] })
      message.success('Ricambio creato con successo')
    },
    onError: () => {
      message.error('Errore durante la creazione del ricambio')
    },
  })
}

export const useUpdatePart = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<PartCreate> }) => {
      const response = await axiosInstance.put<Part>(
        `${API_ENDPOINTS.PARTS}/${id}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['parts'] })
      queryClient.invalidateQueries({ queryKey: ['part', variables.id] })
      message.success('Ricambio aggiornato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'aggiornamento del ricambio')
    },
  })
}

export const useDeletePart = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await axiosInstance.delete(`${API_ENDPOINTS.PARTS}/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parts'] })
      message.success('Ricambio eliminato con successo')
    },
    onError: () => {
      message.error('Errore durante l\'eliminazione del ricambio')
    },
  })
}

export const useLowStockParts = () => {
  return useQuery({
    queryKey: ['parts', 'low-stock'],
    queryFn: async () => {
      const response = await axiosInstance.get<Part[]>(
        `${API_ENDPOINTS.PARTS}/low-stock`
      )
      return response.data
    },
  })
}
