import { useQuery, useMutation } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import type { DatiTargaResponse } from '@/types'

interface MarcheResponse {
  marche: string[]
  count: number
}

interface ModelliResponse {
  marca: string
  modelli: string[]
  count: number
}

interface CarburantiResponse {
  carburanti: string[]
}

/**
 * Hook per ottenere la lista delle marche auto disponibili
 */
export const useMarche = () => {
  return useQuery({
    queryKey: ['auto', 'marche'],
    queryFn: async () => {
      const response = await axiosInstance.get<MarcheResponse>(API_ENDPOINTS.AUTO_MARCHE)
      return response.data
    },
    staleTime: 1000 * 60 * 60 * 24, // 24 ore - dati statici
  })
}

/**
 * Hook per ottenere i modelli di una specifica marca
 */
export const useModelli = (marca: string) => {
  return useQuery({
    queryKey: ['auto', 'modelli', marca],
    queryFn: async () => {
      const response = await axiosInstance.get<ModelliResponse>(
        API_ENDPOINTS.AUTO_MODELLI(marca)
      )
      return response.data
    },
    enabled: !!marca, // Attiva solo quando la marca è selezionata
    staleTime: 1000 * 60 * 60 * 24, // 24 ore
  })
}

/**
 * Hook per ottenere la lista dei tipi di carburante
 */
export const useCarburanti = () => {
  return useQuery({
    queryKey: ['auto', 'carburanti'],
    queryFn: async () => {
      const response = await axiosInstance.get<CarburantiResponse>(API_ENDPOINTS.AUTO_CARBURANTI)
      return response.data.carburanti
    },
    staleTime: 1000 * 60 * 60 * 24, // 24 ore
  })
}

/**
 * Hook mutation per verificare una targa e ottenere i dati del veicolo
 */
export const useVerificaTarga = () => {
  return useMutation({
    mutationFn: async (targa: string): Promise<DatiTargaResponse> => {
      const response = await axiosInstance.post<DatiTargaResponse>(
        API_ENDPOINTS.AUTO_VERIFICA_TARGA,
        { targa: targa.toUpperCase().replace(/\s/g, '') }
      )
      return response.data
    },
  })
}
